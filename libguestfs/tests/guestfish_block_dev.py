from autotest.client.shared import error, utils
from virttest import utils_test

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

    operation = params.get("guestfish_function")
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
                testcase(vm, params)
