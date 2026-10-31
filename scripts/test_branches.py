import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from check_for_updates import compare_manifests
from fetch_app_info import parse_manifests
from update_versions import update_versions_json
from update_game_versions import download_build_version, update_versions_with_game_version, main


def entry(manifest, version=None):
    return {'manifestId': manifest, 'timestamp': '2026-01-01T00:00:00Z', 'gameVersion': version}


class BranchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.versions_file = Path(self.directory.name) / 'versions.json'

    def save(self, data):
        self.versions_file.write_text(json.dumps(data), encoding='utf-8')

    def load(self):
        return json.loads(self.versions_file.read_text(encoding='utf-8'))

    def test_discovery_records_new_branches_without_removing_history(self):
        output = '''SteamCMD output
        "2519830" {
          "depots" {
            "branches" { "alpha-prime" { "buildid" "12" } }
            "2519832" {
              "manifests" {
                "public" { "gid" "101" }
                "release" { "gid" "101" }
                "alpha-prime" { "gid" "202" }
                "pre-splittening" { "gid" "303" }
                "future_branch.2" { "gid" "404" }
              }
              "encryptedmanifests" { "private" { "encrypted_gid_2" "secret" } }
            }
          }
        }'''
        manifests = parse_manifests(output)
        self.assertEqual(manifests, {'2519832': {
            'public': '101', 'release': '101', 'alpha-prime': '202',
            'pre-splittening': '303', 'future_branch.2': '404',
        }})
        previous = {'manifests': {'2519832': {'release': '101', 'old-branch': '99'}}}
        current = {'manifests': manifests}
        changed, changes = compare_manifests(current, previous)
        self.assertTrue(changed)
        self.assertTrue(any("New branch 'alpha-prime'" in change for change in changes))
        self.assertTrue(any("'old-branch' removed" in change for change in changes))
        existing = {'release': [entry('101', 'release-version')], 'old-branch': [entry('99', 'old-version')]}
        self.save(existing)
        self.assertTrue(update_versions_json(current, self.versions_file))
        saved = self.load()
        self.assertEqual(saved['release'], existing['release'])
        self.assertEqual(saved['old-branch'], existing['old-branch'])
        self.assertEqual(saved['public'][0]['manifestId'], '101')
        self.assertEqual(saved['alpha-prime'][0]['manifestId'], '202')
        self.assertIsNone(saved['alpha-prime'][0]['gameVersion'])
        self.assertFalse(update_versions_json(current, self.versions_file))
        self.assertEqual(self.load(), saved)

    def test_new_history_contains_only_discovered_branches(self):
        self.assertTrue(update_versions_json({'manifests': {'2519832': {'new-beta': '123'}}}, self.versions_file))
        self.assertEqual(list(self.load()), ['new-beta'])

    def test_sample_app_info_still_parses(self):
        sample = Path(__file__).parent.parent / 'sample_appid_responce'
        manifests = parse_manifests(sample.read_text(encoding='utf-8'))
        self.assertIn('public', manifests['2519832'])
        self.assertIn('release', manifests['2519832'])

    @patch('update_game_versions.download_build_version')
    def test_all_processes_dynamic_branches_and_preserves_completed_entries(self, download):
        self.save({'release': [entry('1', 'known')], 'alpha-prime': [entry('2')],
                   'pre-splittening': [entry('3')], 'future-beta': [entry('4')]})
        download.side_effect = lambda app, depot, manifest, branch: 'version-' + branch
        self.assertTrue(update_versions_with_game_version(versions_file=self.versions_file))
        self.assertEqual([call.args[3] for call in download.call_args_list],
                         ['alpha-prime', 'pre-splittening', 'future-beta'])
        self.assertEqual(self.load()['release'][0]['gameVersion'], 'known')
        self.assertEqual(self.load()['alpha-prime'][0]['gameVersion'], 'version-alpha-prime')
        download.reset_mock()
        self.assertFalse(update_versions_with_game_version(versions_file=self.versions_file))
        download.assert_not_called()

    @patch('update_game_versions.download_build_version', return_value='alpha-version')
    def test_selected_branch_does_not_update_others(self, download):
        original = {'release': [entry('1')], 'alpha-prime': [entry('2')]}
        self.save(original)
        self.assertTrue(update_versions_with_game_version('alpha-prime', self.versions_file))
        download.assert_called_once_with(2519830, 2519832, '2', 'alpha-prime')
        self.assertEqual(self.load()['release'], original['release'])

    @patch('update_game_versions.download_build_version')
    def test_unknown_branch_fails_without_changing_history(self, download):
        original = {'release': [entry('1')]}
        self.save(original)
        with self.assertRaisesRegex(ValueError, 'Unknown branch'):
            update_versions_with_game_version('typo', self.versions_file)
        download.assert_not_called()
        self.assertEqual(self.load(), original)

    @patch('update_game_versions.download_build_version')
    def test_failed_branch_does_not_block_other_branches(self, download):
        failed_entries = [entry(str(i)) for i in range(4)]
        self.save({'unavailable': failed_entries, 'alpha-prime': [entry('5')]})
        download.side_effect = [None, None, None, 'alpha-version']
        self.assertTrue(update_versions_with_game_version(versions_file=self.versions_file))
        self.assertEqual([call.args[2] for call in download.call_args_list], ['0', '1', '2', '5'])
        self.assertEqual(self.load()['unavailable'], failed_entries)
        self.assertEqual(self.load()['alpha-prime'][0]['gameVersion'], 'alpha-version')

    @patch('update_game_versions.download_build_version')
    def test_success_resets_consecutive_failure_count(self, download):
        self.save({'alpha-prime': [entry(str(i)) for i in range(6)]})
        download.side_effect = [None, None, 'v2', None, None, 'v5']
        self.assertTrue(update_versions_with_game_version(versions_file=self.versions_file))
        self.assertEqual(download.call_count, 6)
        self.assertEqual(self.load()['alpha-prime'][5]['gameVersion'], 'v5')

    def test_downloader_receives_exact_branch_and_headless_key(self):
        def run(command, **kwargs):
            branch = command[command.index('-branch') + 1]
            self.assertNotIn('-beta', command)
            self.assertEqual('-branchpassword' in command, branch == 'headless')
            if branch == 'headless':
                self.assertEqual(command[command.index('-branchpassword') + 1], 'test-key')
            output = Path(command[command.index('-dir') + 1])
            self.assertEqual(Path(command[command.index('-filelist') + 1]).read_text(), 'Build.version\n')
            (output / 'Build.version').write_text('version-' + branch + '\n')
            return SimpleNamespace(returncode=0, stderr='')

        with patch.dict(os.environ, {'STEAM_USERNAME': 'test', 'STEAM_PASSWORD': 'test', 'STEAM_BETA_KEY': 'test-key'}, clear=True), \
                patch('update_game_versions.subprocess.run', side_effect=run) as download:
            for branch in ['public', 'release', 'alpha-prime', 'pre-splittening', 'headless']:
                self.assertEqual(download_build_version(2519830, 2519832, '123', branch), 'version-' + branch)
            self.assertEqual(download.call_count, 5)

    @patch('update_game_versions.update_versions_with_game_version')
    def test_cli_and_workflow_branch_selection(self, update):
        with patch.dict(os.environ, {'STEAM_USERNAME': 'test', 'STEAM_PASSWORD': 'test',
                                     'VERSION_BRANCH': 'alpha-prime'}, clear=True):
            main([])
            update.assert_called_with(branch='alpha-prime')
            main(['--branch', 'pre-splittening'])
            update.assert_called_with(branch='pre-splittening')
            del os.environ['VERSION_BRANCH']
            main([])
            update.assert_called_with(branch='all')


if __name__ == '__main__':
    unittest.main()
