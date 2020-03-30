# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots['test_repository_snap_all_props 1'] = (
    'noop_repo',
    [
        (
            'noop_pipeline',
            None,
            {
            },
            (
                {
                    'Any': (
                        GenericRepr("<ConfigTypeKind.ANY: 'ANY'>"),
                        'Any',
                        'Any',
                        None,
                        None,
                        None,
                        None
                    ),
                    'Array.Shape.67bfeb8716b5a1acfa25db8f46080919cb829774': (
                        GenericRepr("<ConfigTypeKind.ARRAY: 'ARRAY'>"),
                        'Array.Shape.67bfeb8716b5a1acfa25db8f46080919cb829774',
                        None,
                        'List of [{ result?: { json: { path: Path } pickle: { path: Path } } }]',
                        [
                            'Shape.67bfeb8716b5a1acfa25db8f46080919cb829774'
                        ],
                        None,
                        None
                    ),
                    'Bool': (
                        GenericRepr("<ConfigTypeKind.SCALAR: 'SCALAR'>"),
                        'Bool',
                        'Bool',
                        '',
                        None,
                        None,
                        None
                    ),
                    'Float': (
                        GenericRepr("<ConfigTypeKind.SCALAR: 'SCALAR'>"),
                        'Float',
                        'Float',
                        '',
                        None,
                        None,
                        None
                    ),
                    'Int': (
                        GenericRepr("<ConfigTypeKind.SCALAR: 'SCALAR'>"),
                        'Int',
                        'Int',
                        '',
                        None,
                        None,
                        None
                    ),
                    'Path': (
                        GenericRepr("<ConfigTypeKind.SCALAR: 'SCALAR'>"),
                        'Path',
                        'Path',
                        '',
                        None,
                        None,
                        None
                    ),
                    'ScalarUnion.Bool-Selector.931bb6ad8aa201c3e984966c80b27fb6679bef93': (
                        GenericRepr("<ConfigTypeKind.SCALAR_UNION: 'SCALAR_UNION'>"),
                        'ScalarUnion.Bool-Selector.931bb6ad8aa201c3e984966c80b27fb6679bef93',
                        None,
                        None,
                        [
                            'Bool',
                            'Selector.931bb6ad8aa201c3e984966c80b27fb6679bef93'
                        ],
                        None,
                        None
                    ),
                    'ScalarUnion.Float-Selector.c4c3261d2cac02292e67855ef47c83ca58e42529': (
                        GenericRepr("<ConfigTypeKind.SCALAR_UNION: 'SCALAR_UNION'>"),
                        'ScalarUnion.Float-Selector.c4c3261d2cac02292e67855ef47c83ca58e42529',
                        None,
                        None,
                        [
                            'Float',
                            'Selector.c4c3261d2cac02292e67855ef47c83ca58e42529'
                        ],
                        None,
                        None
                    ),
                    'ScalarUnion.Int-Selector.0154da9561ef717b75be37c4edd6ea9051b35a34': (
                        GenericRepr("<ConfigTypeKind.SCALAR_UNION: 'SCALAR_UNION'>"),
                        'ScalarUnion.Int-Selector.0154da9561ef717b75be37c4edd6ea9051b35a34',
                        None,
                        None,
                        [
                            'Int',
                            'Selector.0154da9561ef717b75be37c4edd6ea9051b35a34'
                        ],
                        None,
                        None
                    ),
                    'ScalarUnion.String-Selector.e14649f87c389c8574a39812e1ff7dab2c8c5881': (
                        GenericRepr("<ConfigTypeKind.SCALAR_UNION: 'SCALAR_UNION'>"),
                        'ScalarUnion.String-Selector.e14649f87c389c8574a39812e1ff7dab2c8c5881',
                        None,
                        None,
                        [
                            'String',
                            'Selector.e14649f87c389c8574a39812e1ff7dab2c8c5881'
                        ],
                        None,
                        None
                    ),
                    'Selector.0154da9561ef717b75be37c4edd6ea9051b35a34': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.0154da9561ef717b75be37c4edd6ea9051b35a34',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'value',
                                'Int',
                                True,
                                False,
                                None
                            ),
                            (
                                'json',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            ),
                            (
                                'pickle',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Selector.1bfb167aea90780aa679597800c71bd8c65ed0b2': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.1bfb167aea90780aa679597800c71bd8c65ed0b2',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'enabled',
                                'Shape.da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                False,
                                True,
                                None
                            ),
                            (
                                'disabled',
                                'Shape.da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Selector.5791e3571b37cd1b76c8209bdc3d79a72d2a6bf4': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.5791e3571b37cd1b76c8209bdc3d79a72d2a6bf4',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'in_process',
                                'Shape.f9f75e6f8425e5ade7cf4ddedc20365906ece1ce',
                                False,
                                True,
                                None
                            ),
                            (
                                'multiprocess',
                                'Shape.06565efb671bcb9a7077452fc8341457b5e5a35a',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Selector.931bb6ad8aa201c3e984966c80b27fb6679bef93': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.931bb6ad8aa201c3e984966c80b27fb6679bef93',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'value',
                                'Bool',
                                True,
                                False,
                                None
                            ),
                            (
                                'json',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            ),
                            (
                                'pickle',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Selector.ab6cd856d1a40704c2dc35f9933575746e9479e2': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.ab6cd856d1a40704c2dc35f9933575746e9479e2',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'value',
                                'Any',
                                True,
                                False,
                                None
                            ),
                            (
                                'json',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            ),
                            (
                                'pickle',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Selector.c4c3261d2cac02292e67855ef47c83ca58e42529': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.c4c3261d2cac02292e67855ef47c83ca58e42529',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'value',
                                'Float',
                                True,
                                False,
                                None
                            ),
                            (
                                'json',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            ),
                            (
                                'pickle',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Selector.e0cb7dd427508e37ff80721381a7b2bd1461c866': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.e0cb7dd427508e37ff80721381a7b2bd1461c866',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'in_memory',
                                'Shape.da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                False,
                                True,
                                None
                            ),
                            (
                                'filesystem',
                                'Shape.889b7348071b49700db678dab98bb0a15fd57ecd',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Selector.e14649f87c389c8574a39812e1ff7dab2c8c5881': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.e14649f87c389c8574a39812e1ff7dab2c8c5881',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'value',
                                'String',
                                True,
                                False,
                                None
                            ),
                            (
                                'json',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            ),
                            (
                                'pickle',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6': (
                        GenericRepr("<ConfigTypeKind.SELECTOR: 'SELECTOR'>"),
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'json',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            ),
                            (
                                'pickle',
                                'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.06565efb671bcb9a7077452fc8341457b5e5a35a': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.06565efb671bcb9a7077452fc8341457b5e5a35a',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'config',
                                'Shape.07ed98a1dabc478712c7824678e8c8e52fa1603e',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.07ed98a1dabc478712c7824678e8c8e52fa1603e': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.07ed98a1dabc478712c7824678e8c8e52fa1603e',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'max_concurrent',
                                'Int',
                                False,
                                True,
                                None
                            ),
                            (
                                'retries',
                                'Selector.1bfb167aea90780aa679597800c71bd8c65ed0b2',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.0a7768d17e76e06208229999304ae0357aa8681f': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.0a7768d17e76e06208229999304ae0357aa8681f',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'solids',
                                'Shape.cfd4403245ea53e9035af8ce213022fec90f29bf',
                                False,
                                True,
                                None
                            ),
                            (
                                'storage',
                                'Selector.e0cb7dd427508e37ff80721381a7b2bd1461c866',
                                False,
                                False,
                                None
                            ),
                            (
                                'execution',
                                'Selector.5791e3571b37cd1b76c8209bdc3d79a72d2a6bf4',
                                False,
                                False,
                                None
                            ),
                            (
                                'loggers',
                                'Shape.1174edb63182094c2ffcbba934d04bb6ed7806de',
                                False,
                                True,
                                None
                            ),
                            (
                                'resources',
                                'Shape.da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.0bc7b907090826f16cae49c1d33bd53687cb32bd': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.0bc7b907090826f16cae49c1d33bd53687cb32bd',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'config',
                                'Shape.8bc1d3a8b43942173e047b295c478d1e73fcbcf0',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.1174edb63182094c2ffcbba934d04bb6ed7806de': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.1174edb63182094c2ffcbba934d04bb6ed7806de',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'console',
                                'Shape.0bc7b907090826f16cae49c1d33bd53687cb32bd',
                                False,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.4ce319f0b244b33c363530397798177d6b1ef2ea',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'path',
                                'Path',
                                True,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.67bfeb8716b5a1acfa25db8f46080919cb829774': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.67bfeb8716b5a1acfa25db8f46080919cb829774',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'result',
                                'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6',
                                False,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.889b7348071b49700db678dab98bb0a15fd57ecd': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.889b7348071b49700db678dab98bb0a15fd57ecd',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'config',
                                'Shape.e26e0c525e2d2c66b5a06f4cfdd053de6d44e3ed',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.8bc1d3a8b43942173e047b295c478d1e73fcbcf0': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.8bc1d3a8b43942173e047b295c478d1e73fcbcf0',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'log_level',
                                'String',
                                False,
                                True,
                                None
                            ),
                            (
                                'name',
                                'String',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.8d8e04015d14dbf4adbdf0c6320a01705f25329f': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.8d8e04015d14dbf4adbdf0c6320a01705f25329f',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'retries',
                                'Selector.1bfb167aea90780aa679597800c71bd8c65ed0b2',
                                False,
                                True,
                                None
                            ),
                            (
                                'marker_to_close',
                                'String',
                                False,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.cfd4403245ea53e9035af8ce213022fec90f29bf': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.cfd4403245ea53e9035af8ce213022fec90f29bf',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'noop_solid',
                                'Shape.e9ab42dd7e072d71d5b3be8febf5e4d8022dfc05',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'Shape.da39a3ee5e6b4b0d3255bfef95601890afd80709': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.da39a3ee5e6b4b0d3255bfef95601890afd80709',
                        None,
                        None,
                        None,
                        None,
                        [
                        ]
                    ),
                    'Shape.e26e0c525e2d2c66b5a06f4cfdd053de6d44e3ed': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.e26e0c525e2d2c66b5a06f4cfdd053de6d44e3ed',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'base_dir',
                                'String',
                                False,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.e9ab42dd7e072d71d5b3be8febf5e4d8022dfc05': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.e9ab42dd7e072d71d5b3be8febf5e4d8022dfc05',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'outputs',
                                'Array.Shape.67bfeb8716b5a1acfa25db8f46080919cb829774',
                                False,
                                False,
                                None
                            )
                        ]
                    ),
                    'Shape.f9f75e6f8425e5ade7cf4ddedc20365906ece1ce': (
                        GenericRepr("<ConfigTypeKind.STRICT_SHAPE: 'STRICT_SHAPE'>"),
                        'Shape.f9f75e6f8425e5ade7cf4ddedc20365906ece1ce',
                        None,
                        None,
                        None,
                        None,
                        [
                            (
                                'config',
                                'Shape.8d8e04015d14dbf4adbdf0c6320a01705f25329f',
                                False,
                                True,
                                None
                            )
                        ]
                    ),
                    'String': (
                        GenericRepr("<ConfigTypeKind.SCALAR: 'SCALAR'>"),
                        'String',
                        'String',
                        '',
                        None,
                        None,
                        None
                    )
                }
            ,),
            (
                {
                    'Any': (
                        GenericRepr("<DagsterTypeKind.ANY: 'ANY'>"),
                        'Any',
                        'Any',
                        None,
                        'Any',
                        True,
                        [
                        ],
                        'Selector.ab6cd856d1a40704c2dc35f9933575746e9479e2',
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6'
                    ),
                    'Bool': (
                        GenericRepr("<DagsterTypeKind.SCALAR: 'SCALAR'>"),
                        'Bool',
                        'Bool',
                        None,
                        'Bool',
                        True,
                        [
                        ],
                        'ScalarUnion.Bool-Selector.931bb6ad8aa201c3e984966c80b27fb6679bef93',
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6'
                    ),
                    'Float': (
                        GenericRepr("<DagsterTypeKind.SCALAR: 'SCALAR'>"),
                        'Float',
                        'Float',
                        None,
                        'Float',
                        True,
                        [
                        ],
                        'ScalarUnion.Float-Selector.c4c3261d2cac02292e67855ef47c83ca58e42529',
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6'
                    ),
                    'Int': (
                        GenericRepr("<DagsterTypeKind.SCALAR: 'SCALAR'>"),
                        'Int',
                        'Int',
                        None,
                        'Int',
                        True,
                        [
                        ],
                        'ScalarUnion.Int-Selector.0154da9561ef717b75be37c4edd6ea9051b35a34',
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6'
                    ),
                    'Nothing': (
                        GenericRepr("<DagsterTypeKind.NOTHING: 'NOTHING'>"),
                        'Nothing',
                        'Nothing',
                        None,
                        'Nothing',
                        True,
                        [
                        ],
                        None,
                        None
                    ),
                    'Path': (
                        GenericRepr("<DagsterTypeKind.SCALAR: 'SCALAR'>"),
                        'Path',
                        'Path',
                        None,
                        'Path',
                        True,
                        [
                        ],
                        'Path',
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6'
                    ),
                    'String': (
                        GenericRepr("<DagsterTypeKind.SCALAR: 'SCALAR'>"),
                        'String',
                        'String',
                        None,
                        'String',
                        True,
                        [
                        ],
                        'ScalarUnion.String-Selector.e14649f87c389c8574a39812e1ff7dab2c8c5881',
                        'Selector.fd35cd3159fffc7092f28f6efd65f706953c98f6'
                    )
                }
            ,),
            (
                [
                    (
                        'noop_solid',
                        [
                        ],
                        [
                            (
                                'result',
                                'Any',
                                None,
                                True
                            )
                        ],
                        None,
                        {
                        },
                        [
                        ],
                        None
                    )
                ],
                [
                ]
            ),
            (
                [
                    (
                        'noop_solid',
                        'noop_solid',
                        {
                        },
                        [
                        ]
                    )
                ]
            ,),
            [
                (
                    'default',
                    None,
                    [
                    ],
                    [
                        (
                            'console',
                            'The default colored console logger.',
                            (
                                'config',
                                'Shape.8bc1d3a8b43942173e047b295c478d1e73fcbcf0',
                                False,
                                True,
                                None
                            )
                        )
                    ]
                )
            ]
        )
    ]
)

snapshots['test_repository_snap_empty 1'] = (
    'empty_repo',
    [
    ]
)
