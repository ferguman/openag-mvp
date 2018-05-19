from os import getcwd
from datetime import datetime
from time import sleep
from subprocess import check_call, CalledProcessError, run, PIPE, STDOUT
from sys import path, exc_info
from shutil import copyfile
from logging import getLogger

from config import camera_controller_program, copy_current_image 

logger = getLogger('mvp.' + __name__)

def is_picture_minute(this_instant):

   if camera_controller_program[0] == 'hourly':
      if this_instant.time().minute == camera_controller_program[1]:
         return True
     
   return False

def start_camera_controller(app_state):

   logger.info('Starting camera controller.')

   state = {'hour_of_last_picture':None, 
            'startup':True,
            'hour_of_last_error':None}

   while not app_state['stop']:

      current_state = state

      this_instant = datetime.now() 

      if state['startup'] == True or \
         ((state['hour_of_last_picture'] != this_instant.time().hour) and is_picture_minute(this_instant)):
         
         state['startup'] = False

         file_name = '{:%Y%m%d_%H_%M_%S}.jpg'.format(datetime.utcnow())
         file_location = '{}{}'.format(getcwd() + '/pictures/', file_name) 

         #- camera_shell_command = 'fswebcam -r 1280x720 --no-banner --log syslog {}'.format(file_location)
         camera_shell_command = 'fswebcam -r 1280x720 --no-banner --verbose  --save {}'.format(file_location)
         logger.debug('Preparing to run shell command: {}'.format(camera_shell_command))

         try:
            # Take the picture
            # Figure out if you can suppress fswebcam's output or take the picture using native python code.
            #- picture_results = check_call(camera_shell_command, shell=True)
            #TBD - refactor to run as shell=False. This will make the sytem safer against injection
            # attacks.
            picture_results = run(camera_shell_command, stdout=PIPE, stderr=PIPE, shell=True, check=False)

            if picture_results.returncode == 0 and len(picture_results.stderr) == 0:

                logger.debug('fsweb command success. See the following lines for more info:')
                logger.debug('---return code: {} ...'.format(picture_results.returncode))
                logger.debug('---stderr: {} ...'.format(picture_results.stderr.decode('ascii')))
                logger.debug('---args: {} ...'.format(picture_results.args))
                logger.debug('---stdout: {}'.format(picture_results.stdout.decode('ascii')))

                # Copy the picture to the web directory
                if copy_current_image == True:
                   try:
                      copyfile(file_location, os.getcwd() + '/web/image.jpg')
                      logger.info('Copied latest image file to {}'.format(current_image_copy_location))
                   except:
                      if state['hour_of_last_error'] != this_instant.time().hour:
                         state['hour_of_last_error'] = this_instant.time().hour
                         logger.error("Coudn't copy latest image file to the web directory."
                                      + ' Check fswebcam for proper operations.')
                # Update your current state
                state['hour_of_last_picture'] = this_instant.time().hour
                state['startup'] = False
            else:
               if state['hour_of_last_error'] != this_instant.time().hour:
                  state['hour_of_last_error'] = this_instant.time().hour
                  logger.error('fsweb command failed. See following lines for more info:')
                  logger.error('---return code: {}'.format(picture_results.returncode))
                  logger.error('---stderr: {}'.format(picture_results.stderr.decode('ascii')))
                  logger.error('---args: {}'.format(picture_results.args))
                  logger.error('---stdout: {}'.format(picture_results.stdout.decode('ascii')))

         except CalledProcessError as e:
            if state['hour_of_last_error'] != this_instant.time().hour:
               state['hour_of_last_error'] = this_instant.time().hour
               logger.error('fswebcam call failed with the following results: {}'.format(exc_info()[0]))
         except:
            if state['hour_of_last_error'] != this_instant.time().hour:
               state['hour_of_last_error'] = this_instant.time().hour
               logger.error('Camera error: {}'.format(exc_info()[0]))
            
      sleep(1)  
