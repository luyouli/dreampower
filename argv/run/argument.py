import re
from json import JSONDecodeError

from utils import load_json


def arg_altered(parser):
    parser.add_argument(
        "-a",
        "--altered",
        help="Path of the directory where steps images transformation are write."
    )

def arg_export_step(parser):
    parser.add_argument(
        "--export-step",
        type=int,
        help="Export step image."
             "Steps are : \n"
             "0 : dress -> correct [OPENCV]\n"
             "1 : correct -> mask [GAN]\n"
             "2 : mask -> maskref [OPENCV]\n"
             "3 : maskref -> maskdet [GAN]\n"
             "4 : maskdet -> maskfin [OPENCV]\n"
             "5 : maskfin -> nude [GAN]"
    )

def arg_export_step_path(parser):
    parser.add_argument(
        "--export-step-path",
        help="Path of the directory where export the step image."
    )


def arg_auto_rescale(parser):
    parser.add_argument(
        "--auto-rescale",
        action="store_true",
        help="Scale image to 512x512.",
    )


def arg_auto_resize(parser):
    parser.add_argument(
        "--auto-resize",
        action="store_true",
        help="Scale and pad image to 512x512 (maintains aspect ratio).",
    )


def arg_auto_resize_crop(parser):
    parser.add_argument(
        "--auto-resize-crop",
        action="store_true",
        help="Scale and crop image to 512x512 (maintains aspect ratio).",
    )


def arg_color_transfer(parser):
    parser.add_argument(
        "--color-transfer",
        action="store_true",
        help="Transfers the color distribution from the input image to the output image."
    )


def arg_cpu(parser):
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force photo processing with CPU (slower)",
    )


def arg_gpu(parser):
    parser.add_argument(
        "--gpu",
        action="append",
        type=int,
        help="ID of the GPU to use for processing. "
             "It can be used multiple times to specify multiple GPUs "
             "(Example: --gpu 0 --gpu 1 --gpu 2). Default : 0"
    )


def arg_gan_persistent(parser):
    parser.add_argument(
        "--disable-persistent-gan",
        action="store_true",
        help="Disable persistent in memory gan model."
             "Reduce memory usage but increase computation time on multiple processing."
    )


def arg_ignore_size(parser):
    parser.add_argument(
        "--ignore-size",
        action="store_true",
        help="Ignore image size checks."
    )


def arg_input(parser):
    parser.add_argument(
        "-i",
        "--input",
        help="Path or http(s) url of the photo. Or path of the directory to transform .",
    )


def arg_json_args(parser):
    def check_json_args_file():
        def type_func(a):
            try:
                j = load_json(a)
            except JSONDecodeError:
                raise parser.error(
                    "Arguments json {} is not in valid JSON format.".format(a))
            return j
        return type_func

    parser.add_argument(
        "-j",
        "--json-args",
        type=check_json_args_file(),
        help="Load arguments from json files or json string. "
             "If a command line argument is also provide the json value will be ignore for this argument.",
    )


def arg_json_folder_name(parser):
    parser.add_argument(
        "--json-folder-name",
        default="settings.json",
        help="Path to the json per folder configuration to looks for when processing folder. Default: settings.json"
    )


def arg_n_core(parser):
    parser.add_argument(
        "--n-cores",
        type=int,
        default=4,
        help="Number of cpu cores to use. Default : 4",
    )


def arg_n_run(parser):
    parser.add_argument(
        "-n",
        "--n-runs",
        type=int,
        default=1,
        help="Number of times to process input. Default : 1"
    )


def arg_output(parser):
    parser.add_argument(
        "-o",
        "--output",
        help="Path of the file or the directory where the transformed photo(s) "
             "will be saved. Default : output<input extension>"
    )


def arg_overlay(parser):
    def check_crops_coord():
        def type_func(a):
            if not re.match(r"^\d+,\d+:\d+,\d+$", a):
                raise parser.error("Incorrect coordinates format. "
                                   "Valid format is <x_top_left>,"
                                   "<y_top_left>:<x_bot_right>,<x_bot_right>.")
            return tuple(int(x) for x in re.findall(r'\d+', a))

        return type_func

    parser.add_argument(
        "--overlay",
        type=check_crops_coord(),
        help="Processing the part of the image given by the coordinates "
             "(<x_top_left>,<y_top_left>:<x_bot_right>,<x_bot_right>) and overlay the result on the original image."
    )


def arg_preferences(parser):
    parser.add_argument(
        "--bsize",
        type=float,
        default=1,
        help="Boob size scalar best results 0.3 - 2.0",
    )

    parser.add_argument(
        "--asize",
        type=float,
        default=1,
        help="Areola size scalar best results 0.3 - 2.0",
    )

    parser.add_argument(
        "--nsize",
        type=float,
        default=1,
        help="Nipple size scalar best results 0.3 - 2.0",
    )

    parser.add_argument(
        "--vsize",
        type=float,
        default=1,
        help="Vagina size scalar best results 0.3 - 1.5",
    )

    parser.add_argument(
        "--hsize",
        type=float,
        default=0,
        help="Pubic hair size scalar best results set to 0 to disable",
    )


def arg_step(parser):
    def check_steps_args():
        def type_func(a):
            if not re.match(r"^[0-5]:[0-5]$", a):
                raise parser.error("Incorrect skip format. "
                                   "Valid format is <starting step>:<ending step>.\n"
                                   "Steps are : \n"
                                   "0 : dress -> correct [OPENCV]\n"
                                   "1 : correct -> mask [GAN]\n"
                                   "2 : mask -> maskref [OPENCV]\n"
                                   "3 : maskref -> maskdet [GAN]\n"
                                   "4 : maskdet -> maskfin [OPENCV]\n"
                                   "5 : maskfin -> nude [GAN]"
                                   )

            steps = tuple(int(x) for x in re.findall(r'\d+', a))

            if steps[0] > steps[1]:
                raise parser.error("The ending step should be greater than starting the step.")

            return steps[0], steps[1] + 1

        return type_func

    parser.add_argument(
        "-s",
        "--steps",
        type=check_steps_args(),
        help="Select a range of steps to execute <starting step>:<ending step>."
             "Steps are : \n"
             "0 : dress -> correct [OPENCV]\n"
             "1 : correct -> mask [GAN]\n"
             "2 : mask -> maskref [OPENCV]\n"
             "3 : maskref -> maskdet [GAN]\n"
             "4 : maskdet -> maskfin [OPENCV]\n"
             "5 : maskfin -> nude [GAN]"
    )
