resource "aws_s3_bucket" "this" {
  count = "${var.create ? 1 : var.problem_var}"

  bucket                 = "${var.bucket}"
  region                 = "${var.region}"
  acl                    = "${var.acl}"
  versioning             = "${var.versioning}"
}
