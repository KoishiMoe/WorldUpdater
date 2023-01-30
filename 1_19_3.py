"""
A simple script to upgrade your existing world to 1.20
License: MIT
"""


import os.path
import random
import string
from typing import Union

import nbtlib
from nbtlib.tag import Compound, List, String


def main(path: str = '', backup: bool = True, dry_run: bool = False, update_1_20: bool = True, bundle: bool = True):
    path = path if not os.path.isdir(path) else os.path.join(path, 'level.dat')
    try:
        f = nbtlib.load(path)  # we do not use the context manager here because it will automatically save the file
    except FileNotFoundError:
        print("Please specify a valid path to the level.dat file.")
        return

    try:
        # Get the data
        data: Compound = f['Data']

        # Print basic information
        print('Level name: {}'.format(data['LevelName']))
        print('Version: {}'.format(data['Version']['Name']))

    except KeyError:
        print("Seems like the file is corrupted or not a valid level.dat file.")
        return

    # Get the data
    datapacks: Union[Compound, dict] = data.get('DataPacks', {})
    enabled_packs: List[String] = datapacks.get('Enabled', List[String]())
    disabled_packs: List[String] = datapacks.get('Disabled', List[String]())
    enabled_features: List[String] = data.get('enabled_features', List[String]())

    # Add vanilla datapack and features
    if 'minecraft:vanilla' not in enabled_features:
        print("Adding vanilla features...")
        enabled_features.append(String('minecraft:vanilla'))
    if not ('minecraft:vanilla' in enabled_packs or 'vanilla' in enabled_packs):
        print("Adding vanilla datapack...")
        enabled_packs.append(String('vanilla'))

    # Update 1.20
    if update_1_20:
        if 'minecraft:update_1_20' not in enabled_features:
            print('Adding "minecraft:update_1_20" to enabled_features...')
            enabled_features.append(String('minecraft:update_1_20'))
        if 'update_1_20' in disabled_packs:
            print('Removing "update_1_20" from disabled datapacks...')
            disabled_packs.remove('update_1_20')
        if 'update_1_20' not in enabled_packs:
            print('Adding "update_1_20" to enabled datapacks...')
            enabled_packs.append(String('update_1_20'))

    # Bundle
    if bundle:
        if 'minecraft:bundle' not in enabled_features:
            print('Adding "minecraft:bundle" to enabled_features...')
            enabled_features.append(String('minecraft:bundle'))
        if 'bundle' in disabled_packs:
            print('Removing "bundle" from disabled datapacks...')
            disabled_packs.remove('bundle')
        if 'bundle' not in enabled_packs:
            print('Adding "bundle" to enabled datapacks...')
            enabled_packs.append(String('bundle'))

    # Save the file
    if not dry_run:
        # Backup the file
        if backup:
            backup_name = '{}-{}.bak'. \
                format(os.path.basename(path), ''.join(random.choice(string.ascii_uppercase) for i in range(5)))
            f.save(os.path.join(os.path.dirname(path), backup_name))
            print('Backup saved as {}'.format(backup_name))

        data['DataPacks'] = nbtlib.Compound({'Enabled': enabled_packs, 'Disabled': disabled_packs})
        data['enabled_features'] = enabled_features
        f.save()
        print('Done!')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Add 1.19.3\'s experimental features to a world.')
    parser.add_argument('path', type=str, nargs='?', default='',
                        help='The path to the level.dat file')
    parser.add_argument('--no-backup', dest='backup', action='store_false',
                        help='Do not backup the file')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help='Do not save the file')
    parser.add_argument('--no-update-1-20', dest='update_1_20', action='store_false',
                        help='Do not add update_1_20 to the world')
    parser.add_argument('--no-bundle', dest='bundle', action='store_false',
                        help='Do not add bundle to the world')
    args = parser.parse_args()
    main(**vars(args))
