#!/usr/bin/env python

import sys
import subprocess
import argparse
import uuid
import time
import pickle
import logging
import logging.handlers

from pathlib import Path
from collections import namedtuple
from typing import List
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format = '%(asctime)s %(process)d %(module)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger("assas_data_uploader." + __name__)

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
        resume: bool,
        user: str,
        name: str,
        description: str,
        source_path: str,
        astec_archive_paths: List[str],
        target_path: str = '/lsdf/kit/scc/projects/ASSAS/upload_test',
    ) -> None:
        
        self.folder_command = ['ssh', f'{user}@os-login.lsdf.kit.edu', f'mkdir -v {target_path}/{upload_uuid}']
        self.upload_command = ['rsync', '-avP', f'{source_path}', f'{user}@os-login.lsdf.kit.edu:{target_path}/{upload_uuid}']      
        self.notify_command = ['ssh', f'{user}@os-login.lsdf.kit.edu', f'touch {target_path}/{upload_uuid}/{upload_uuid}']
        self.stat_command = ['ssh', f'{user}@os-login.lsdf.kit.edu', f'ls -l {target_path}/{upload_uuid}']
        
        self.save_upload_info(
            upload_uuid=upload_uuid,
            user=user,
            name=name,
            description=description,
            source_path=source_path,
            astec_archive_paths=astec_archive_paths,
        )
        
        start_time = time.time()
        
        if not resume:
            logger.info(f'Create new folder on server {target_path}/{upload_uuid}.')
            self.execute_sub_process_log_stdout(self.folder_command)
        else:
            logger.info(f'Update existing folder on server {target_path}/{upload_uuid}.')
        
        self.execute_sub_process_log_stdout(self.upload_command)
        
        end_time = time.time()        
        duration_in_seconds = end_time - start_time
        duration_string = AssasDataUploader.get_duration(duration_in_seconds)
        logger.info(f'Upload took {duration_string}.')
        
        if not resume:
            logger.info(f'Notify new upload (upload_uuid = {upload_uuid}).')
            self.execute_sub_process_log_stdout(self.notify_command)
        else:
            logger.info(f'Skip notification (upload_uuid = {upload_uuid}).')
        
        logger.info(f'Content of uploaded archive:')
        self.execute_sub_process_log_stdout(self.stat_command)
   
    def save_upload_info(
        self,
        upload_uuid: str,
        user: str,
        name: str,
        description: str,
        source_path: str,
        astec_archive_paths: List[str],
        update_file_name: str = 'upload_info.pickle',
    )-> None:
        
        upload_info = {}
        upload_info['upload_uuid'] = upload_uuid
        upload_info['user'] = user
        upload_info['name'] = name
        upload_info['description'] = description
        upload_info['archive_paths'] = astec_archive_paths
        
        logger.info(f'Dump upload information into {source_path}/{update_file_name}.')
        with open(f'{source_path}/{update_file_name}', 'wb') as file:
            pickle.dump(upload_info, file)
        
        logger.info(f'Upload information:')
        for key, value in upload_info.items():
            logger.info(f'{key}: {value}')
    
    def execute_sub_process_log_stdout(
        self,
        command_list: List[str]
    )-> bool:

        try:
            
            process = subprocess.Popen(command_list, stdout=subprocess.PIPE)
            logger.debug(f'Execute command_list {command_list}.')
            
            while process.poll() is None:
                line = process.stdout.readline()
                logger.debug(str(line))
        
        except e:
            
            logger.error(f'Caught exeption when executing command: {str(e)}.')
            raise

    @staticmethod
    def get_duration(
        seconds
    )-> Duration:
        
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        
        return Duration(weeks, days, hours, minutes, seconds)


def list_of_strings(arg):
    
    return arg.split(', ')
    
if __name__ == "__main__":
    
    instance_uuid = uuid.uuid4()
    
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
    
    user = args.user
    name = args.name
    description = args.description
    source_path = args.source
    archive_paths = args.archives
    
    resume = False
    if args.uuid is None:
        upload_uuid = str(instance_uuid)
    else:
        upload_uuid = args.uuid
        resume = True

    file_handler = logging.FileHandler(f'{upload_uuid}_assas_data_uploader.log', 'a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)

    AssasDataUploader(
        upload_uuid=upload_uuid,
        resume = resume,
        user=user,
        name=name,
        description=description,
        source_path=source_path,
        astec_archive_paths=archive_paths
    )