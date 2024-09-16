
import subprocess
import argparse
import uuid
import time
import pickle

from pathlib import Path
from collections import namedtuple
from typing import List

class Duration(namedtuple('Duration', 'weeks, days, hours, minutes, seconds')):
    
    def __str__(
        self
    )-> str:
        
        return ', '.join(self._get_formatted_units())

    def _get_formatted_units(
        self
    )-> str:
        
        for unit_name, value in self._asdict().items():
            if value > 0:
                if value == 1:
                    unit_name = unit_name.rstrip('s')
                yield '{} {}'.format(value, unit_name)

class AssasDataUploader:
    
    def __init__(
        self,
        upload_uuid: str,
        user: str,
        name: str,
        description: str,
        source_path: str,
        astec_archive_paths: List[str],
        target_path: str = '/lsdf/kit/scc/projects/ASSAS/upload_test',
    ) -> None:
        
        new_upload = False
        
        if upload_uuid is None:
            self.upload_uuid = str(uuid.uuid4())
            new_upload = True
            print(f'Generate new upload uuid {self.upload_uuid}')
        else:
            self.upload_uuid = upload_uuid
            print(f'Use existing upload_uuid {self.upload_uuid}')
                
        self.user = user
        self.name = name
        self.description = description
        self.source_path = source_path
        self.astec_archive_paths = astec_archive_paths
        self.target_path = target_path
                
        self.create_folder_command = ['ssh', f'{self.user}@os-login.lsdf.kit.edu', f'mkdir -v {target_path}/{self.upload_uuid}']
        self.upload_command = ['rsync', '-avP', f'{source_path}', f'{self.user}@os-login.lsdf.kit.edu:{target_path}/{self.upload_uuid}']        
        self.notify_command = ['ssh', f'{self.user}@os-login.lsdf.kit.edu', f'echo "{self.upload_uuid}" >> {target_path}/uploads/uploads.txt']
        
        self.save_upload_info()
        
        start_time = time.time()
        
        if new_upload:
            print('Create new folder on server')
            self.create_folder_on_server()
        
        self.upload_archive()
        
        end_time = time.time()
        
        duration_in_seconds = end_time - start_time
        duration_string = AssasDataUploader.get_duration(duration_in_seconds)
               
        print(f'Upload took {duration_string}')
        
        if new_upload:
            print('Notify new upload')
            self.notify_upload()
   
    def save_upload_info(
        self        
    )-> None:
        upload_info = {}
        upload_info['upload_uuid'] = self.upload_uuid
        upload_info['user'] = self.user
        upload_info['name'] = self.name
        upload_info['description'] = self.description
        upload_info['archive_paths'] = self.astec_archive_paths
        
        with open(f'{source_path}/upload_info.pickle', 'wb') as file:
            pickle.dump(upload_info, file)
        
        print(f'Upload information:')
        for key, value in upload_info.items():
            print(f'{key}: {value}')
   
    def execute_command(
        self,
        command_list: List[str]
    )-> bool:
        
        try:
            with subprocess.Popen(command_list) as process: process.wait()
        except:
            return False
        
        return True
    
    @staticmethod
    def get_duration(
        seconds
    )-> Duration:
        
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        
        return Duration(weeks, days, hours, minutes, seconds)
    
    def upload_archive(
        self
    )-> bool:
        
        return self.execute_command(self.upload_command)
    
    def create_folder_on_server(
        self
    )-> bool:

        return self.execute_command(self.create_folder_command)
    
    def notify_upload(
        self
    )-> bool:
        
        return self.execute_command(self.notify_command)

def list_of_strings(arg):
    
    return arg.split(', ')
    
if __name__ == "__main__":
    
    argparser = argparse.ArgumentParser()
    
    argparser.add_argument(
        '-u',
        '--user',
        type=str,
        help='user name with access to LSDF',
        required=True,
    )    
    
    argparser.add_argument(
        '-s',
        '--source',
        type=str,
        help='source path of astec archive',
        required=True,
    )
    
    argparser.add_argument(
        '-n',
        '--name',
        type=str,
        help='name of the corresponding astec archives',
        required=True,
    )
        
    argparser.add_argument(
        '-d',
        '--description',
        type=str,
        help='description of the corresponding astec archives',
        required=True,
    )
    
    argparser.add_argument(
        '-a',
        '--archives',
        type=list_of_strings,
        help='sub path of astec binary archive',
        required=True,  
    )
    
    argparser.add_argument(
        '-i',
        '--uuid',
        type=str,
        help='uuid of upload in case of resuming an upload',
        required=False,
        default=None
    )
    
    args = argparser.parse_args()
    
    upload_uuid = args.uuid
    user = args.user
    name = args.name
    description = args.description
    source_path = args.source
    archive_paths = args.archives
    
    AssasDataUploader(
        upload_uuid=upload_uuid,
        user=user,
        name=name,
        description=description,
        source_path=source_path,
        astec_archive_paths=archive_paths
    )
