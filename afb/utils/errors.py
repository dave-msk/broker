# Copyright 2019 Siu-Kei Muk (David). All Rights Reserved.
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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six

from afb.utils import types


class StructMismatchError(Exception):
  pass


def validate_is_callable(obj, name):
  if not six.callable(obj):
    raise ValueError("`{}` must be a callable. Given: {}".format(name, obj))


def validate_type(obj, cls, name):
  if obj is not None and not isinstance(obj, cls):
    raise TypeError("\"{}\" must be of type \"{}\". Given: {}"
                    .format(name, cls.__name__, type(obj)))


def validate_args(input_args, all_args):
  inv_args = set(input_args) - set(all_args)
  if inv_args:
    raise ValueError("Invalid arguments.\n"
                     "Expected: {}\nGiven: {}\nInvalid: {}."
                     .format(sorted(all_args),
                             sorted(input_args),
                             sorted(inv_args)))


def validate_rqd_args(input_args, rqd_args):
  missing = set(rqd_args) - set(input_args)
  if missing:
    raise TypeError("Missing required arguments.\n"
                    "Required: {}\nGiven: {}\nMissing: {}"
                    .format(sorted(rqd_args),
                            sorted(input_args),
                            sorted(missing)))

  inv_args = {k for k, v in six.iteritems(input_args)
              if k in rqd_args and v is None}
  if inv_args:
    raise ValueError("Required arguments must not be None.\n"
                     "Required: {}\nGiven: {}\nInvalid: {}"
                     .format(sorted(rqd_args),
                             sorted(input_args),
                             sorted(inv_args)))


def validate_kwargs(obj, name):
  if obj is None:
    return
  if not isinstance(obj, dict):
    raise TypeError("`{}` must be a dictionary of keyword arguments. "
                    "Given {}".format(name, type(obj)))
  inv_keys = []
  for k in obj:
    if not isinstance(k, six.string_types):
      inv_keys.append(k)
  if inv_keys:
    raise TypeError("Keys in `{}` must be of string type. Given: {}"
                    .format(name, inv_keys))


def validate_struct(type_spec, struct):
  # `list` case
  if isinstance(type_spec, list) and isinstance(struct, list):
    for s in struct:
      validate_struct(type_spec[0], s)
    return

  # `dict` case
  if isinstance(type_spec, dict) and isinstance(struct, dict):
    k_spec, v_spec = next(six.iteritems(type_spec))
    for ks, vs in six.iteritems(struct):
      validate_struct(k_spec, ks)
      validate_struct(v_spec, vs)
    return

  # `tuple` case
  if isinstance(type_spec, tuple) and isinstance(struct, tuple):
    if len(type_spec) != len(struct):
      # TODO: Add descriptive error message
      raise StructMismatchError("Input parameter structure must conform"
                                " to type specification.\n"
                                "Required: {}\nGiven: {}"
                                "Required length of input: {}\n"
                                "Given length of input: {}"
                                .format(type_spec, struct,
                                        len(type_spec), len(struct)))
    for t_spec, s in zip(type_spec, struct):
      validate_struct(t_spec, s)
    return

  # Direct type case
  if isinstance(type_spec, type):
    if (struct is None) or \
       (isinstance(struct, type_spec)) or \
       (types.is_obj_spec(struct)):
      return
    # TODO: Add descriptive error message
    raise TypeError("The input must be one of the following:\n"
                    "1. None; \n"
                    "2. An instance of expected type; \n"
                    "3. An object specification. (singleton `dict` mapping a "
                    "factory to its arguments for instantiation)\n"
                    "Required: {}\nGiven: {}"
                    .format(type_spec, struct))

  # None of the valid cases matches.
  # TODO: Add descriptive error message
  raise StructMismatchError("Input parameters are not aligned with"
                            " required structure.\n"
                            "Required: {}\nGiven: {}"
                            .format(type_spec, struct))


def validate_type_spec(type_spec):
  if isinstance(type_spec, list) and len(type_spec) == 1:
    validate_type_spec(type_spec[0])
    return
  if isinstance(type_spec, dict) and len(type_spec) == 1:
    k, v = next(six.iteritems(type_spec))
    validate_type_spec(k)
    validate_type_spec(v)
    return
  if isinstance(type_spec, tuple):
    for s in type_spec:
      validate_type_spec(s)
    return
  if isinstance(type_spec, type):
    return
  raise ValueError("The type specification must be either of the following:\n"
                   "1. Singleton `dict` where the key and value are both "
                   "type specifications;\n"
                   "2. Singleton `list`, where the content is a "
                   "type specification; \n"
                   "3. `tuple` of type specifications; or\n"
                   "4. A class or type.\n"
                   "Given: {}".format(type_spec))
