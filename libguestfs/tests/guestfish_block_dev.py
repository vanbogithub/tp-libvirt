from autotest.client.shared import error, utils
from virttest import utils_test, utils_misc, data_dir
from virttest.tests import unattended_install
import logging
import shutil
import os


def test_blockdev_flushbufs(vm, params):
    """
    1) Write a tempfile on host
    2) Copy file to guest with virt-tar-in
    3) Delete created file
    4) Check file on guest
    """

    params["image_path"] = utils_test.libguestfs.preprocess_image(params)

    if params.get("image_path") is None:
        raise error.TestFail("Image could not be created for some reason.")

    gf = utils_test.libguestfs.GuestfishTools(params)
    creates, createo  = gf.create_fs()
    if creates is False:
        gf.close_session()
        raise error.TestFail(createo)
    gf.close_session()

    gf = utils_test.libguestfs.GuestfishTools(params)
    image_path = params.get("image_path")
    gf.add_drive(image_path)
    gf.run()
    pv_name = params.get("pv_name")
    gf_result = gf.blockdev_flushbufs(pv_name)
    logging.debug(gf_result)
    if gf_result.exit_status:
        gf.close_session()
        raise error.TestFail("blockdev_flushbufs failed.")
    logging.info("Get readonly status successfully.")
    gf.close_session()

    add_ref = params.get("guestfs_add_ref", "disk")
    run_mode = params.get("guestfs_run_mode", "interactive")

    if run_mode == "interactive":
        if add_ref == "disk":
            pass
        elif add_ref == "remote":
            pass
        else:
            raise error.TestFail("Invalid parameter guestfs_add_ref = %s" % add_ref)
    elif run_mode == "remote":
        pass
    else:
        raise error.TestFail("Invalid parameter guestfs_run_mode = %s" % run_mode)

def image_copy(params):
    image = '%s.%s' % (params['image_name'], params['image_format'])
    image_name = os.path.basename(image)
    src = params.get('images_good')
    dst = '%s/%s' % (data_dir.get_data_dir(), image)
    mount_point = params.get("dst_dir")

    utils_misc.mount(src, mount_point, "nfs", perm="ro")
    image_src = utils_misc.get_path(mount_point, image_name)
    logging.debug("Copying image %s to %s", image_src, dst)
    shutil.copy(image_src, dst)
    utils_misc.umount(src, mount_point, "nfs")


def run(test, params, env):
    """
    Test of built-in block_dev related commands in guestfish.

    1) Get parameters for test
    2) Set options for commands
    3) Run key commands:
       a.add disk or domain with readonly or not
       b.launch
       c.mount root device
    4) Write a file to help result checking
    5) Check result
    """

    vm_name = params.get("main_vm")
    vm = env.get_vm(vm_name)

    if vm.is_alive():
        vm.destroy()

    operation = params.get("guestfish_function")
    testcase = globals()["test_%s" % operation]
    partition_types = params.get("partition_types")
    fs_types = params.get("fs_types")
    image_formats = params.get("image_formats")

#    image_copy(params)

    for image_format in image_formats.split(" "):
        params["image_format"] = image_format
        for partition_type in partition_types.split(" "):
            params["partition_type"] = partition_type
            for fs_type in fs_types.split(" "):
                params["fs_type"] = fs_type
                testcase(vm, params)


