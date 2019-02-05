# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Unit tests for `tensorboard.manager`."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import json
import re

import six
import tensorflow as tf

from tensorboard import manager
from tensorboard import version


def _make_info(i=0):
  """Make a sample TensorboardInfo object.

  Args:
    i: Seed; vary this value to produce slightly different outputs.

  Returns:
    A type-correct `TensorboardInfo` object.
  """
  return manager.TensorboardInfo(
      version=version.VERSION,
      start_time=datetime.datetime.fromtimestamp(1548973541 + i),
      port=6060 + i,
      pid=76540 + i,
      path_prefix="/foo",
      logdir="~/my_data/",
      db="",
      cache_key="asdf",
  )


class TensorboardInfoTest(tf.test.TestCase):
  """Unit tests for TensorboardInfo typechecking and serialization."""

  def test_roundtrip_serialization(self):
    # This will also be tested indirectly as part of `manager`
    # integration tests.
    info = _make_info()
    also_info = manager._info_from_string(manager._info_to_string(info))
    self.assertEqual(also_info, info)

  def test_serialization_rejects_bad_types(self):
    info = _make_info()._replace(start_time=1549061116)  # not a datetime
    with six.assertRaisesRegex(
        self,
        ValueError,
        "expected 'start_time' of type.*datetime.*, but found: 1549061116"):
      manager._info_to_string(info)

  def test_serialization_rejects_wrong_version(self):
    info = _make_info()._replace(version="reversion")
    with six.assertRaisesRegex(
        self,
        ValueError,
        "expected 'version' to be '.*', but found: 'reversion'"):
      manager._info_to_string(info)

  def test_deserialization_rejects_bad_json(self):
    bad_input = "parse me if you dare"
    with six.assertRaisesRegex(
        self,
        ValueError,
        "invalid JSON:"):
      manager._info_from_string(bad_input)

  def test_deserialization_rejects_non_object_json(self):
    bad_input = "[1, 2]"
    with six.assertRaisesRegex(
        self,
        ValueError,
        re.escape("not a JSON object: [1, 2]")):
      manager._info_from_string(bad_input)

  def test_deserialization_rejects_missing_version(self):
    info = _make_info()
    json_value = json.loads(manager._info_to_string(info))
    del json_value["version"]
    bad_input = json.dumps(json_value)
    with six.assertRaisesRegex(
        self,
        ValueError,
        "incompatible version:"):
      manager._info_from_string(bad_input)

  def test_deserialization_rejects_bad_version(self):
    info = _make_info()
    json_value = json.loads(manager._info_to_string(info))
    json_value["version"] = "not likely"
    bad_input = json.dumps(json_value)
    with six.assertRaisesRegex(
        self,
        ValueError,
        "incompatible version:.*not likely"):
      manager._info_from_string(bad_input)

  def test_deserialization_rejects_extra_keys(self):
    info = _make_info()
    json_value = json.loads(manager._info_to_string(info))
    json_value["unlikely"] = "story"
    bad_input = json.dumps(json_value)
    with six.assertRaisesRegex(
        self,
        ValueError,
        "bad keys on TensorboardInfo"):
      manager._info_from_string(bad_input)

  def test_deserialization_rejects_missing_keys(self):
    info = _make_info()
    json_value = json.loads(manager._info_to_string(info))
    del json_value["start_time"]
    bad_input = json.dumps(json_value)
    with six.assertRaisesRegex(
        self,
        ValueError,
        "bad keys on TensorboardInfo"):
      manager._info_from_string(bad_input)

  def test_deserialization_rejects_bad_types(self):
    info = _make_info()
    json_value = json.loads(manager._info_to_string(info))
    json_value["start_time"] = "2001-02-03T04:05:06"
    bad_input = json.dumps(json_value)
    with six.assertRaisesRegex(
        self,
        ValueError,
        "expected 'start_time' of type.*int.*, but found:.*"
        "'2001-02-03T04:05:06'"):
      manager._info_from_string(bad_input)



if __name__ == "__main__":
  tf.test.main()
