import ee
ee.Initialize()

fcCars = ee.FeatureCollection('users/diimanut/SIMEX/BASES/SIGEF_INCRA_2020')
expFloAM = ee.FeatureCollection('users/diimanut/SIMEX/BASES/EXPLORACAO_FLORESTAL_AM')
expFloRR = ee.FeatureCollection('users/diimanut/SIMEX/BASES/EXPLORACAO_FLORESTAL_RR')
simexPa = ee.FeatureCollection('users/diimanut/SIMEX/BASES/EXTRACAO_MADEIREIRA_PA')
simexAM = ee.FeatureCollection('users/diimanut/SIMEX/BASES/SIMEX_AM')
simexRO = ee.FeatureCollection('users/diimanut/SIMEX/BASES/SIMEX_RO')
simexMtLegal = ee.FeatureCollection('users/diimanut/SIMEX/BASES/EXTRACAO_MADEIREIRA_LEGAL_MT')
simexMtIlegal = ee.FeatureCollection('users/diimanut/SIMEX/BASES/EXTRACAO_MADEIREIRA_ILEGAL_MT')
autex_ro = ee.FeatureCollection('users/diimanut/SIMEX/BASES/PONTOS_AUTEX_RO')
carPa = ee.FeatureCollection('projects/terras/terras_monitoramento/tables/SALES/CAR_IMAFLORA_PA_2018')
forestryConcessions = ee.FeatureCollection('users/diimanut/SIMEX/BASES/FORESTRY_CONCESSIONS')
auxLayers = {
    13: {
        0: [1, 2, 3,4],
        1: {
            1:
            {
                1: expFloAM,
                2: 'EXPLORACAO_FLORESTAL_AM',
                3: { 'palette': '#DAA520', 'opacity': 0.8 }
            }
        },
        2: {
            1:
            {
                1: simexAM,
                2: 'SIMEX_AM',
                3: { 'palette': '#FF0000', 'opacity': 0.8 }
            }
        },
        3: {
            1:
            {
                1: forestryConcessions,
                2: 'FORESTRY_CONCESSIONS',
                3: { 'palette': '#6A5ACD', 'opacity': 0.8 }
            }
        },
        4:{
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    },
    11: {
        0: [1, 2, 3,4],
        1: {
            1:
            {
                1: autex_ro,
                2: 'PONTOS_AUTEX_RO',
                3: { 'palette': '#FF6347', 'opacity': 0.8 }
            }
        },
        2: {
            1:
            {
                1: simexRO,
                2: 'SIMEX_RO',
                3: { 'palette': '#FF0000', 'opacity': 0.8 }
            }
        },
        3: {
            1:
            {
                1: forestryConcessions,
                2: 'FORESTRY_CONCESSIONS',
                3: { 'palette': '#6A5ACD', 'opacity': 0.8 }
            }
        },
        4:{
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }

    },
    15: {
        0: [1, 2, 3, 4, 5, 6,7],
        1: {
            1: {
                1: simexPa.filterMetadata('Categoria', 'equals', 'legal'),
                2: 'SIMEX_PA_AUTHORIZED',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        },
        2: {
            1: {
                1: simexPa.filterMetadata('Categoria', 'equals', 'Ilegal'),
                2: 'SIMEX_PA_NON_AUTHORIZED',
                3: { 'palette': '#FF6347', 'opacity': 0.8 }
            }
        },
        3: {
            1: {
                1: carPa,
                2: 'CAR_PA',
                3: { 'palette': '#FFD700', 'opacity': 0.8 }
            }
        },
        4: {
            1: {
                1: ee.FeatureCollection('users/diimanut/SIMEX/BASES/SIMEX_PA_AUTHORIZED_19'),
                2: 'SIMEX_PA_AUTHORIZED_19',
                3: { 'palette': '#8B0000', 'opacity': 0.8 }
            }
        },
        5: {
            1: {
                1: ee.FeatureCollection('users/diimanut/SIMEX/BASES/PMFS_PA'),
                2: 'PMFS_PA',
                3: { 'palette': '#483D8B', 'opacity': 0.8 }
            }
        },
        6: {
            1:
            {
                1: forestryConcessions,
                2: 'FORESTRY_CONCESSIONS',
                3: { 'palette': '#6A5ACD', 'opacity': 0.8 }
            }
        },
        7:{
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#6959CD', 'opacity': 0.8 }
            }
        }
    },
    14: {
        0: [1, 2,3],
        1: {
            1: {
                1: expFloRR,
                2: 'EXPLORACAO_FLORESTAL_RR',
                3: { 'palette': '#FF6347', 'opacity': 0.8 }
            }
        },
        2: {
            1:
            {
                1: forestryConcessions,
                2: 'FORESTRY_CONCESSIONS',
                3: { 'palette': '#6A5ACD', 'opacity': 0.8 }
            }
        },
        3:{
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    },
    51: {
        0: [1, 2, 3,4],
        1: {
            1: {
                1: simexMtLegal,
                2: 'SIMEX_MT_AUTHORIZED',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        },
        2: {
            1: {
                1: simexMtIlegal,
                2: 'SIMEX_MT_NON_AUTHORIZED',
                3: { 'palette': '#FF6347', 'opacity': 0.8 }
            }
        },
        3: {
            1:
            {
                1: forestryConcessions,
                2: 'FORESTRY_CONCESSIONS',
                3: { 'palette': '#6A5ACD', 'opacity': 0.8 }
            }
        },
        4:{
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    },
    17: {
        0: [1],
        1: {
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    },
    16: {
        0: [1],
        1: {
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    },
    21: {
        0: [1],
        1: {
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    },
    12: {
        0: [1],
        1: {
            1: {
                1: fcCars,
                2: 'SIGEF_INCRA_2020',
                3: { 'palette': '#7B68EE', 'opacity': 0.8 }
            }
        }
    }

}

dicAuxState =   {'RO':11,'AC':12,'AM':13,'RR':14,'PA': 15,'AP':16,'TO':17,'MA': 21,'MT':51}
    