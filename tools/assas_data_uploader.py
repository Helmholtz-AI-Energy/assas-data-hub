
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
    ):
        
        for unit_name, value in self._asdict().items():
            if value > 0:
                if value == 1:
                    unit_name = unit_name.rstrip('s')
                yield '{} {}'.format(value, unit_name)

class AssasDataUploader:
    
    def __init__(
        self,
        user: str,
        source_path: str,
        runs: int = 1,
        target_path: str = '/lsdf/kit/scc/projects/ASSAS/upload_test'
    ) -> None:
        
        self.upload_id = str(uuid.uuid4())
        self.runs = runs
        self.source_path = source_path
        
        self.create_folder_command = ['ssh', f'{user}@os-login.lsdf.kit.edu', f'mkdir -v {target_path}/{self.upload_id}']
        self.upload_command = ['rsync', '-avP', f'{source_path}', f'{user}@os-login.lsdf.kit.edu:{target_path}/{self.upload_id}']
        
        self.save_upload_info()
        
        start_time = time.time()
        
        self.create_folder_on_server()
        self.upload_archive()
        
        end_time = time.time()
        
        duration_in_seconds = end_time - start_time
        duration_string = AssasDataUploader.get_duration(duration_in_seconds)
               
        print(f'Upload took {duration_string}')
        
    def save_upload_info(
        self        
    ):
        upload_info = {}
        upload_info['upload_id'] = self.upload_id
        upload_info['runs'] = self.runs
        
        with open(f'{source_path}/upload_info.pickle', 'w') as file:
            pickle.dump(upload_info, file)
   
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
        '-r',
        '--runs',
        type=int,
        help='indicates if source path contains several runs',
        default=1,
    )
    
    args = argparser.parse_args()
    
    user = args.user
    source_path = args.source
    runs = args.runs
  
    AssasDataUploader(
        user=user,
        source_path=source_path,
        runs=runs
    )      