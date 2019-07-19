module "tests" {
  source = "../tests"

  providers = {
    aws = "aws"
  }

  acl = "${local.acl}"
  bucket = "${local.bucket}"
  create_2 = "${local.create_2}"
  create_keystore_bucket = "${local.create_keystore_bucket}"
  now_a_var = "${local.now_a_var}"
  org_ids = "${local.org_ids}"
  prefix = "${local.prefix}"
  problem_var = "${local.problem_var}"
  region = "${local.region}"
  tags = "${local.tags}"
  versioning = "${local.versioning}"
}

