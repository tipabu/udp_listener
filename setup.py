# Copyright (c) 2020 Tim Burke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

setuptools.setup(
    name="udp_listener",
    author="Tim Burke",
    author_email="tim.burke@gmail.com",
    url="https://github.com/tipabu/udp_listener",
    version="1.0",
    description="A little UDP server to listen for things like StatsD metrics",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development",
    ],
    py_modules=["udp_listener"],
    entry_points={
        "console_scripts": [
            "udp-listener = udp_listener:main"
        ]
    },
)
