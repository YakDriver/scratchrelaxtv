provider "aws" {
  region  = "${var.region}"
}

data "aws_iam_policy_document" "this" {
  count = "${var.create_keystore_bucket ? 1 : 0}"

  statement {
    sid = "AllowOrgObjectActions"

    principals {
      type = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "arn:aws:s3:::${var.bucket}/${var.prefix}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"
      values   = [var.org_ids]
    }
  }
}

resource "aws_s3_bucket" "this" {
  count = "${var.create_2 ? 1 : var.problem_var}"

  bucket                 = "${var.bucket}"
  region                 = "${var.region}"
  acl                    = "${var.acl}"
  policy                 = "${data.aws_iam_policy_document.this.json}"
  versioning             = "${var.versioning}"
  tags                   = "${var.tags}"
  acceleration_status    = "var.now_a_var"
}
