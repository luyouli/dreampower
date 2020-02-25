"""Image Transform Processing."""
import os
import sys
import hashlib

from config import Config as Conf
from processing import Processing
from processing.utils import select_phases
from processing.worker import run_worker
from utils import camel_case_to_str, write_image
from loader import Loader


class ImageProcessing(Processing):
    """Image Processing Class."""
    def _setup(self, *args):
        """
        Process Image Constructor.

        :param args: <dict> args parameter to run the image transformation (default use Conf.args)
        """
        self.__phases = select_phases(self._args)
        self.__input_path = self._args['input']
        self.__output_path = self._args['output']
        self.__altered_path = self._args.get('altered')
        self.__starting_step = self._args['steps'][0] if self._args.get('steps') else 0
        self.__ending_step = self._args['steps'][1] if self._args.get('steps') else None

        Conf.log.debug("All Phases : {}".format(self.__phases))
        Conf.log.debug("To Be Executed Phases : {}".format(self.__phases[self.__starting_step:self.__ending_step]))

        imagename_no_ext = os.path.splitext(os.path.basename(self.__input_path))[0]
        if (self._args.get('folder_altered')):
            folder_name = imagename_no_ext + '_' + str(hashlib.md5(open(self.__input_path, 'rb').read()).hexdigest())
            folder_path = os.path.join(self._args['folder_altered'], folder_name)

            if (not os.path.isdir(folder_path)):
               os.makedirs(folder_path, exist_ok=True)

            self._args['folder_altered'] = folder_path
            path = self._args['folder_altered']

            self.__image_steps = [self.__input_path] + [
                os.path.join(path, "{}.png".format(p().__class__.__name__))
                for p in self.__phases[:self.__starting_step]
            ]
        elif (self.__altered_path):
            folder_name = imagename_no_ext + '_' + str(hashlib.md5(open(self.__input_path, 'rb').read()).hexdigest())
            folder_path = os.path.join(self.__altered_path, folder_name)

            if (not os.path.isdir(folder_path)):
               os.makedirs(folder_path, exist_ok=True)

            self.__altered_path = folder_path
            path = self.__altered_path

            self.__image_steps = [self.__input_path] + [
                os.path.join(path, "{}.png".format(p().__class__.__name__))
                for p in self.__phases[:self.__starting_step]
            ]
        else:
            # TODO: refactor me, please!
            self.__image_steps = [self.__input_path] + [
                self.__input_path
                for p in self.__phases[:self.__starting_step]
            ]

        Conf.log.info("Processing on {}".format(str(self.__image_steps)))


        try:
            self.__image_steps = [
                (Loader.get_loader(x)).load(x) if isinstance(x, str) else x for x in self.__image_steps
            ]
        except (FileNotFoundError, AttributeError) as e:
            Conf.log.error(e)
            Conf.log.error("{} is not able to resume because it not able to load required images. "
                           .format(camel_case_to_str(self.__class__.__name__)))
            Conf.log.error("Possible source of this error is that --altered argument is not a correct "
                           "directory path that contains valid images.")
            sys.exit(1)

    def _execute(self, *args):
        """
        Execute all phases on the image.

        :return: None
        """
        # todo: refactor me, please!
        # with this we force the auto-resize for dreamtime, but it is far from ideal
        #if self.__starting_step == 5:
        #    r = run_worker(self.__phases[0], self.__image_steps, config=self._args)
        #    self.__image_steps.append(r)

        for step,p in enumerate(x for x in self.__phases[self.__starting_step:self.__ending_step]):
            r = run_worker(p, self.__image_steps, config=self._args)
            self.__image_steps.append(r)

            # todo: refactor me, please!
            if self._args.get('export_step'):
                export_step = self._args.get('export_step')

                if self._args.get('overlay'):
                    export_step += 2
                    #Conf.log.debug("Fixing overlay export_step = {}".format(export_step))

                if self._args.get('auto_rescale') or self._args.get('auto_resize') or self._args.get('auto_resize_crop'):
                    export_step += 1
                    #Conf.log.debug("Fixing scale export_step = {}".format(export_step))

                if export_step == (step-1):
                    step_path = self._args.get('export_step_path') or os.path.abspath(os.path.join(self.__output_path, '..', 'export.png'))

                    if self._args.get('overlay'):
                        r = run_worker(self.__phases[-1], self.__image_steps, config=self._args)

                    write_image(r, step_path)

                    Conf.log.debug("Export Step Image Of {} Execution: {}".format(
                        camel_case_to_str(p.__name__),
                        step_path
                    ))

            if self.__altered_path:
                if (self._args.get('folder_altered')):
                    path = self._args['folder_altered']
                else:
                    path = self.__altered_path

                write_image(r, os.path.join(path, "{}.png".format(p.__name__)))

                Conf.log.debug("{} Step Image Of {} Execution".format(
                    os.path.join(path, "{}.png".format(p.__name__)),
                    camel_case_to_str(p.__name__),
                ))

        write_image(self.__image_steps[-1], self.__output_path)
        Conf.log.info("{} Created".format(self.__output_path))
        Conf.log.debug("{} Result Image Of {} Execution"
                       .format(self.__output_path, camel_case_to_str(self.__class__.__name__)))

        return self.__image_steps[-1]
