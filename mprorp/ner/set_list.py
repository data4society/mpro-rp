# 30 sets
# 1-29 sets contains 1250 docs,
# last set - 391 doc
sets1250 = ['1b8f7501-c7a8-41dc-8b06-fda7d04461a2',
            'da587fba-bacb-4a84-8717-cc2c21280373',
            '8acb6f3f-89bf-464f-b5f4-b7317ed3422e',
            'd73c41ea-86f7-4735-97f3-a4772409de47',
            'bed4a75f-c779-49ed-ada8-6d539635683e',
            '1d071a5f-1919-4807-b168-b7d4a321d3d7',
            '49581438-4e1c-436f-985a-bec805d226ba',
            'de2f7f06-f277-44a7-bcec-55a468549295',
            '338316c7-4389-4c67-adec-9aef6ca8e470',
            '79300537-02f8-4f48-afb9-4da206fa8ece',
            '94fe03a9-2cd8-42f1-8e6b-6670a4263b89',
            '3fedc9a5-2e25-4841-8091-c028e65854f5',
            '546466df-599e-4f5f-9d4f-f9721cca1986',
            '01e08b77-67ef-4f76-b43d-82a5b17a5c05',
            '9cb78ad6-741d-4af2-89e4-bae023ac4d7e',
            'fcda13c2-9182-4f66-ba25-f7652e3c67ca',
            '76183814-ab26-45a8-9593-bb94d48bacff',
            '7ac6900c-4356-4f18-a054-bc5ecb971184',
            'f9ecfadc-89ce-4d64-b5f2-127d98ffdf1c',
            '4e5abcb3-2f34-4468-9c68-00b3cf84fa2b',
            '6f58a05e-720a-4262-8dfe-dbb86cc3e842',
            'efbde158-bbbe-4f99-bed5-baa3c5398320',
            'ee9e6018-164f-4742-b587-68d96c4cbd63',
            '309d2b37-914d-441a-9722-19e7a1dc530e',
            'cb04f2fb-e66c-4d94-b18b-16cb9efdeb9f',
            'c349032b-ba3c-4fb8-a888-39869fad05de',
            '7f6ff022-9cd3-41b0-9457-8d7057de4d28',
            'd7b056df-4341-4e8a-967c-6b9bdb5557b9']

tr_com = '265fac6f-4b3e-466d-b7fe-fcdc90978a4e'
tr_com100 = 'c0b20817-e5f2-4fcb-bd39-ef1f53b403a3'
test_com = '5544e81e-6dda-458f-9f79-e40d990e6e94'
    
set_2 = {
    'dev_160': '9e0473dd-6f9d-4ddc-8740-5f39ae802d8f',
    'dev_320': '03dda1ba-2ca9-45a2-b733-849302d41695',
    'dev_640': 'ce01ddaa-ed6a-420c-b299-260b422ee4b0',
    'dev_1280': 'd23f021d-c6eb-41f7-a79c-162ef7a0cdf3',
    'train_640': '96e47d8a-3a8a-4879-a05a-83b98a23fdf3',
    'train_1280': '153b3ccc-9a9f-42cc-8c5b-d3b74ffbd1ca',
    'train_2560': '152efaac-ce6a-4107-aad6-364f7cb787bf',
    'train_5120': '62405eef-32e0-4999-99bf-ae64dd511f18',
    'all_8323': 'd2ddb0d7-964e-40ef-b518-1584f193c906'
}

set_factRuEval = {
    'devset': 'bb2f6bdb-646e-43f3-8187-764ea53cec08',
    'testset': '13397370-c96e-429d-b558-45796e9baf3c',
    '50': 'e83cd768-4c5f-4bb4-a796-fcf491c1ec80',
    '204': '11982c03-4002-4fc7-b045-f56ef8d3207e'
}

set_news = {'train': '4fb42fd1-a0cf-4f39-9206-029255115d01',
            'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}

set34751 = 'bbdec1ac-4589-46b9-b33e-e40ef527dbc9'

sets = dict()
sets['1'] = {
    'tr_id_pn': '1f413604-d6a7-4acb-a060-77cf6a6ddd19', # pos + neg
    'tr_id_pnc': '858a0631-42b5-40d4-b446-e457ea1d4ff7', # pos + neg + com
    'tr_id_pc': 'a0596a43-99fa-411e-a447-1cfc07a36b53', # pos + com
    'tr_id_pc100': '7111ef46-9f8d-4ca4-a9c9-50a837d39116',
    'test_positive': '77aa00f2-81b7-40d5-8bac-c9d7755d2b2e',
    'test_negative': '377cdb8c-ccf0-4f2f-8fe6-17289709b0b1',
    'tr_pos': '042b0854-b213-4987-8568-11ddde77d461',
    'tr_neg': '47fe435c-f7c9-4a5c-9379-71b33c29a06a',
    'test_pn': 'a467dd1d-8028-4446-b9d7-203b773b375c'
}
sets['2'] = {
    'tr_id_pn': 'b75dc32c-0b20-4dbc-af87-3bb2a24e5938', # pos + neg
    'tr_id_pnc': '5f128ce8-2c82-4ccd-a4a5-4b09c7c91ea5', # pos + neg + com
    'tr_id_pc': '908f2892-0b67-48c0-bc47-d128bfa0cd3f', # pos + com
    'tr_id_pc100': '829d2db3-3ec2-4c4a-b986-9e2e3deaaee1',
    'test_positive': 'c1293b5e-d1d4-4567-b6fa-c5a830c60d6a',
    'test_negative': 'ce6a4102-1f11-4811-a5c7-e2d8ef7c2231',
    'tr_pos': 'd23977ef-2dd2-46b2-84da-9b23b8ff71de',
    'tr_neg': 'f5989784-24f4-46e7-9b73-887c23bdd344',
    'test_pn': '63f12eb5-fa8b-4dff-b2d8-27ada121dcc0'
}
sets['3'] = {
    'tr_id_pn': 'c5498c2f-b11a-4094-97fb-6e002f6c3a52', # pos + neg
    'tr_id_pnc': 'bfc3d5ab-0d1c-4531-b333-84712b0c0113', # pos + neg + com
    'tr_id_pc': '90898161-57dc-4ce7-8239-ef3a7b1cd2d1', # pos + com
    'tr_id_pc100': '06c530b3-a8e9-4d08-9883-128689996f7b',
    'test_positive': '848408ce-b69d-4d6d-8360-795f183303a0',
    'test_negative': 'f1dc071f-6c71-4a18-bc10-0273f1b69952',
    'tr_pos': '916f13a2-4d43-4bdc-ba52-ed9feadfe387',
    'tr_neg': '105ca410-7d84-4eff-9e45-9b8c29507bb6',
    'test_pn': 'a65e5faf-c46e-485b-bc5b-1c8ebe54efeb'
}
sets['4'] = {
    'tr_id_pn': 'c020af3c-1e0e-403f-8ffc-8ff2c974c907', # pos + neg
    'tr_id_pnc': '19bb2c5f-a609-44da-b96e-448918d08d19', # pos + neg + com
    'tr_id_pc': '83fdb43a-7a31-4831-b675-ca2f6439df13', # pos + com
    'tr_id_pc100': 'c020af3c-1e0e-403f-8ffc-8ff2c974c907',
    'test_positive': '45f2309c-096f-47bc-b19c-fff7b58a2de5',
    'test_negative': '5f8e26d9-0067-4d18-be6b-36ccd8a8df74',
    'tr_pos': '6e98a44d-66f1-4d7f-adaa-83a77126b748',
    'tr_neg': '23d197c3-467e-49d8-8a07-5336ec2b18fe',
    'test_pn': 'a5a0f8db-ae75-4055-a080-e93ac6c81b39'
}
sets['5'] = {
    'tr_id_pn': '3bfb9d28-ee48-4021-857c-8d9e916a70d2', # pos + neg
    'tr_id_pnc': 'c4b9b04a-0686-4541-b247-8d2e8e28bdbc', # pos + neg + com
    'tr_id_pc': '7d02ca6c-fe4b-4a8c-abb4-e833529dedb4', # pos + com
    'tr_id_pc100': '27ecb9c4-9e7e-4805-b3dd-846a0512b848',
    'test_positive': 'e28daae0-f239-4bf1-a9af-8e4070d83f26',
    'test_negative': 'b7b645d0-c7d8-4c4c-8bed-9f7be061bcfe',
    'tr_pos': '98601bf3-84ce-47d3-8002-bb7355a23280',
    'tr_neg': '0382d97e-1806-4abd-8897-c143ba0f3a9b',
    'test_pn': '59090417-e05c-4151-99d0-9e8432a22288'
}
sets['6'] = {
    'tr_id_pn': '09b95033-6fe8-4df9-89e5-9472cbd2f573',
    'tr_id_pnc': 'c5b4dc5b-04a5-4255-807c-655f6817bdee',
    'tr_id_pc': 'd2b6d3ec-b533-4702-8afd-c3365141119e',
    'tr_id_pc100': 'e44f56ac-893a-4d2c-97e8-2746ab758517',
    'test_positive': 'c2f7f817-6fed-4b0a-9a3e-014614405e7e',
    'test_negative': '70bc5194-2073-4c0a-a783-86ffb4fa9fd4',
    'tr_pos': '9939f387-d3aa-4a9c-be37-064bf844db2d',
    'tr_neg': '3e936aff-a728-4b63-90f4-3f516d02560f',
    'test_pn': '0706a451-d995-41d4-af9b-e8e0451ca465'
}
sets['04'] = {
    'tr_id_pn': 'e9a40771-88fd-4060-8a17-55c49f30925f', # pos + neg
    'tr_id_pnc': 'c9047cad-2784-4251-b55f-e4d3507b4d38', # pos + neg + com
    'tr_id_pc': 'e262d71b-bc9f-4de6-9841-c1719524a757', # pos + com
    'tr_id_pc100': 'ad425b5d-c22c-4502-8d4a-a62f4b12b8cc',
    'test_positive': '53d0f42a-9f48-4a54-9293-434ad108eacb',
    'test_negative': 'aeb689e7-a28c-4adf-a4ff-82ab343d761b',
    'tr_pos': '5969de73-831f-4714-9d86-50aded34ba18',
    'tr_neg': 'e4855bc6-c528-4bcc-8faf-e9e625856cff',
    'test_pn': '9574e5a5-9f6d-45a0-b50a-9680a8e2385f'
}
sets['06'] = {
    'tr_id_pn': 'f2a966a4-16a0-431b-84ab-6518137c94c2', # pos + neg
    'tr_id_pnc': 'd8566fd9-a2fa-4f5f-8e35-38703d0e6f4c', # pos + neg + com
    'tr_id_pc': '3873aeb3-f70f-440f-9037-af127dd4e00d', # pos + com
    'tr_id_pc100': '2ddca0d4-b514-4979-87fe-6d6826791cd6',
    'test_positive': '25eb5af9-8021-40ea-ab69-bd95adc6d752',
    'test_negative': 'd1e5dadb-f5bf-4cd5-9ce9-841bd1b71eb8',
    'tr_pos': '8c20da89-a46f-4b52-9411-e07f3c198bd2',
    'tr_neg': 'f35f33ca-c363-4f6f-a0fa-cad89345107c',
    'test_pn': '9f380071-151e-41ed-bcdb-5c8d69002970'
}
sets['11'] = {'new': 'ac9ea1cb-7b43-43ea-9a53-1ef968744299',
              'positive': 'b90e65c3-f862-4fb6-80b1-e6b8b3f126eb',
              'tr_pos_set': '9fa77db8-ef1e-43c0-9c00-a5379e0b05af',
              'test_pos_set': '4df1a71e-1e96-4031-a168-51df23979f15',
              'tr_set_2': '5bd69ab2-0c94-4f01-b77d-18013158f6ae', # по сравнению с tr_set и test_set уменьшено
              'test_set_2': '3ba807af-55a8-4732-aa8c-7df926b24243',# количество отрицательных документов для баланса
              'tr_set': '99b17109-40a9-4240-abdf-108a7df2605c',
              'test_set': '69086ef1-79b7-475f-b9c7-8e034bde04e5'}
sets['12'] = {'new': '10e44b91-9a3d-4f23-ad28-820a239a7a9e',
              'positive': 'edd6958b-6ec5-4fd3-b481-02a48679d00e',
              'tr_pos_set':   '6aed5a36-36c5-4da3-b7f0-0f38a9019861',
              'test_pos_set': '1155916c-b2c8-4c1d-a1d2-1f46ba1bb535',
              'tr_set_2': '9a11eb49-1c04-4017-98c7-c304851114ef',
              'test_set_2': '4cf38918-2b60-4c70-ac23-c7b2471a2515',
              'tr_set':       'b8e4d2dd-3270-47c7-bae6-288aefc16564',
              'test_set':     '2719c865-db49-49d2-8c1b-54730bccb7c5' }
sets['13'] = {'new': 'b3cd2c8e-24b5-4559-b64a-e1eb6cad7cad',
              'positive': 'bf1a3429-96a1-4209-bb0d-05d132e68351',
              'tr_pos_set': 'cd409090-16ca-49ac-a4a9-1a9f6f537f38',
              'test_pos_set': 'd78e518c-f5f1-4ef3-b3ca-f721eb3592e5',
              'tr_set_2': '83c44917-1328-43e9-ad93-030e9639f75c',
              'test_set_2': 'e94b1b8a-d27a-4136-a225-bba2e79e8d67',
              'tr_set': '66ee0f08-f3f6-42d6-a478-5224185feaa7',
              'test_set': '474eb9c0-1f0d-4a80-b610-bdf2f1a9623c'}
sets['14'] = {'new': 'dd262fc2-7d65-4c2f-b101-19216aae7ae9',
              'positive': '72c7a020-0874-4cb3-a223-ebc7ec20584b',
              'tr_pos_set': '2382885c-c3d2-46b8-9985-af8e51617365',
              'test_pos_set': '335706be-37f3-446c-8f11-442895dcb39a',
              'tr_set_2': '9e3881b3-f3db-42d1-adca-35d23a21646a',
              'test_set_2': 'c7b3a042-109b-4906-b5f0-6a9375fa732b',
              'tr_set': 'becd972f-e26b-4361-a049-58a54b8d67cc',
              'test_set': '34eb33b3-c593-4096-a965-42de8c60532f'}
sets['15'] = {'new': 'a3073be1-5470-4720-a379-8e20bf6fe505',
              'positive': '9fc9dcfd-cd8c-4e9f-8054-f038f536e64a',
              'tr_pos_set': '72ce51fb-41bd-40c8-9701-a3fcce0d711b',
              'test_pos_set': '5755fda2-4bee-4b6e-bdb3-5cd912eadc91',
              'tr_set_2': '56a63fa1-08da-4fe6-b503-720582a1c7f9',
              'test_set_2': '6cec9beb-ab1c-454d-b03d-42134587b743',
              'tr_set': '7f0c0a6d-ddf0-48b4-88bf-06846ff87f2d',
              'test_set': '5d2abf1c-b9f4-4362-a8a6-60fd0ec5c82f'}
sets['16'] = {'new':          '8e90e65a-25e4-493b-beda-3bb920c230d1',
              'positive':     '6a1ea451-6bf9-4529-a816-75fae78569c2',
              'tr_pos_set':   'ff27a310-226b-41d3-acfc-d9b7e9069148',
              'test_pos_set': '9f6d0dbc-804f-46f5-87a3-dcefb167af80',
              'tr_set_2': '9038069d-f579-46bd-9ace-7e1e226ea609',
              'test_set_2': '6e481c09-36a9-4ca7-a8cc-fb42c7e72098',
              'tr_set':       '70e6ec17-2a60-41b0-adcd-e8360cdc0792',
              'test_set':     '8ae5bd11-77ce-4718-9045-8e0967460260'}

sets['21'] = {'new': 'b3b88f50-26f9-43a9-90ff-487870ffb91b',  # 41 docs
              'positive': '1bb42f73-9fa2-46f2-8311-89433ffe1924',
              'tr_set': 'efd003c8-05d9-4315-a0e1-10fde45085df',  # 150+150
              'test_set': '9519a4b6-227e-4c0b-9423-5cfebe3d1cd8'}  # 38+38
sets['22'] = {'new': 'b96a5a35-01af-48e7-b622-39c7b046b0d0',  # 29 docs
              'positive': '9d4aa521-5161-4cff-98fe-4347cfa381c7',
              'tr_set':       'f3609b13-40a6-4183-9c41-c28665b37050',  # 174+174
              'test_set':     'd41e0291-e09f-4f7b-95ab-97295d6d2eca'}  # 44+44
sets['23'] = {'new': '3f6f6b23-440f-4f2f-a71d-1bed5c12178b',  # 96 docs
              'positive': '2d85888a-0945-4c23-9d1d-7075ac542781',
              'tr_set': 'fccec914-7e15-4b0d-b8c4-204160241d85',  # 252+252
              'test_set': 'c6b07d17-6fdf-4d13-a58f-f6e0bb2f6910'}  # 63+63
sets['24'] = {'new': '2f434c8d-f19a-4627-ac4b-b9ba731bdc50',  # 270 docs
              'positive': 'd3788c44-dd6e-48c0-b6c0-48d694bb58b5',
              'tr_set': '047d8774-0229-44fd-ad73-6911691e4eaa',  # 393+393
              'test_set': '208d2688-5798-47be-8ae5-d10062024dc7'}  # 98+98
sets['25'] = {'new': '4577146d-f585-45ab-bd52-b6c94576e977',  # 45 docs
              'positive': 'b3b39503-2797-4093-a36e-159ab2ab8523',
              'tr_set': '7aca0c27-2e3a-4838-abd3-a646f9708287',  # 216+216
              'test_set': '52769a4a-b276-420e-9ecb-fdc76be4997e'}  # 54+54
sets['26'] = {'new':          'a5130989-cf38-448a-85a1-07c3cfe7aaa2',  # 195 docs
              'positive':     'fbab2d72-0901-4fa6-a9d3-e421e9fe39d4',
              'tr_set':       '35936517-90e1-4058-a517-e120264e6e13',  # 383+383
              'test_set':     '8d2f81fc-dab3-457a-b363-fd0eaea97fea'}  # 96+96

sets['negative'] = {'all':   '779bd1d0-887c-4c81-bfc5-8b4632f9b81e',
                    'train': '2009195a-2c4a-4120-88ac-147464a9ccb5',
                    'test':  '2b4be3c1-b217-4e3e-a4a7-8ab3fc767d7d',
                    'new2': '96a1ff65-cebb-4de9-b095-3797736e609d'  # created 26/05/17 - status 74
                    }
sets['pp'] = {'train_set': '0364c8e3-ebcd-4fa2-b14a-3f10c498bcd3',
              'test_set':  'dca01625-d655-4900-9b32-6a548c7dc0dd',
              'new2': 'ba701270-1f60-4ed4-9cc4-d98bb3d8f842',  # 167 docs
              }

sets['ss'] = {'train_set': '69565f15-73ea-4d06-84aa-d3e5cea57ee7',
              'test_set':  '498aac37-efd8-4b9c-932a-17d6291a2ab6',
              'new2': 'c81c8f13-e285-4889-9f39-d2cdb24d0084'  # 314 docs
              }

rubrics = {
    '1': {'pos': '10180591-8d58-4d6e-a3dd-cc7df1cbb671',
          'neg': 'ec434320-3a42-4bbc-aa2f-fb95dc28e9db'},# искусство
    '2': {'pos': '264468df-6c20-4a66-8f4f-07c91f200e37',
          'neg': '49596f63-353a-4207-a076-4ca0bd66eca3'},# отчисление и увольнение
    '3': {'pos': '8676d718-7ca7-49a4-a815-8bc2efd9ee2e',
          'neg': 'd4a52335-34f7-4677-a20b-21b39983088a'},# насилие
    '4': {'pos': 'c1486c39-62f5-4476-aca0-6641af0ba11d',
          'neg': '4c5882dc-0dd1-4382-813b-18fb02650e02'},# ЛГБТ
    '5': {'pos': 'd9b9f38e-77e0-4ab5-8a58-98e8ff5e6d21',
          'neg': '6aac7df6-98a5-42e1-a463-4c7f222269a8'},# угрозы
    '6': {'pos': 'f079f081-d1ab-4136-ba4f-520ac59b70b8',
          'neg': 'a283ced3-32b5-4ae4-a9a6-440107c3e9e2'},# интернет
    'pp': {'pos': '14e511c0-2ce9-49b2-9d0c-f16c383765d1'},
    'ss': {'pos': 'db9baa28-e201-47a6-aada-14f44f42e98f'},
}
rubric_names = {
    '1': 'iskustvo',
    '2': 'uvolnenie',
    '3': 'nasilie',
    '4': 'lgbt',
    '5': 'ugrozy',
    '6': 'internet',
    'pp': 'politpress',
    'ss': 'svoboda slova'
}