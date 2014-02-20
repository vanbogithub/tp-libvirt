import logging
import os
from virttest import data_dir, utils_test



def test_aug_clear(vm, params):
    """
    Set the value associated with path to NULL. This is the same as the augtool(1) clear command.

    1) Create a new augeas handle
    2) Clear augeas path
    3) Look up the value of the augeas path
    """
    logging.info("START FUNCTION: test_aug_clear")
    params["disk_img"] = utils_test.libguestfs.preprocess_image(params)
    gf = utils_test.libguestfs.GuestfishTools(params)

    #add drive in read-only mode
    add_drive_result = gf.add_drive_ro(gf.disk_img)
    if add_result.exit_status:
        gf.close_session()
        raise error.TestFail("Can not add drive %s" % gf.disk_img)
    logging.info("Add drive %s successfully" % gf.disk_img)

    #Launch
    run_result = gf.run()
    if run_result.exit_status:
        gf.close_session()
        raise error.TestFail("Can not launch: %s" % run_result)
    logging.info("Launch successfully")

    #mount the device
    mount_point = params["mount_point"]
    mount_result = gf.mount_options("noatime", mount_point, "/")
    if mount_result.exit_status:
        gf.close_session()
        raise error.TestFail("Can not mount %s to /" % mount_point)
    logging.info("mount %s to / successfully" % mount_point)

    aug_init_result = gf.aug_init("/", "0")
    if aug_init_result.exit_status:
        gf.close_session()
        raise error.TestFail("Can not create a augeas handle")
    logging.info("Create augeas handle successfully")

    aug_clear_result = gf.aug_clear("/files/etc/passwd/root/home")
    if aug_clear_result.exit_status:
        gf.close_session()
        raise error.TestFail("Can not clean augeas path")
    logging.info("Clear augeas path successfully")

    aug_get_result = gf.inner_cmd("-aug-get /files/etc/passwd/root/home")
    if aug_get_result.exit_status:
        gf.close_session()
        raise error.TestFail("Should not look up the value of an augeas path after aug-clear")
    logging.info("Clean augeas path successfully")

    logging.info("END FUNCTION: test_aug_clear")


def run(test, params, env):
    """
    Test of built-in augeas related commands in guestfish

    1) Get parameters for test
    2) Set options for commands
    3) Run key commands:
       a. add disk or domain with readonly or not
       b. launch
       c. mount root device
    4)run augeaus APIs inside guestfish session

    """

    vm_name = params.get("main_vm")
    vm = env.get_vm(vm_name)

    operation = params.get("guestfish_operation")
    testcase = globals()["test_%s" % operation]
    partition_types = params.get("partition_types")
    fs_types = params.get("fs_types")
    image_formats = params.get("image_formats")


    for image_format in image_formats.split(" "):
        params["image_format"] = image_format
        for partition_type in partition_types.split(" "):
            params["partition_type"] = partition_type
            for fs_type in fs_types.split(" "):
                params["fs_type"] = fs_type
                utils_libguestfs.preprocess(params)
                testcase(vm, params)
