from bs4 import BeautifulSoup
import pytest
from unittest.mock import patch

from sagikoza import core

@pytest.fixture
def k_pubstype_01_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_01_detail_1(k_pubstype_01_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2505-9900-0335",
            "pn": "375438",
            "p_id": "03",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 3
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '0b3e19acc3672f0a76019eaa6d2e50b8bc63c1e9be883809e212f8ccdbc939b0',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '二二八', 
            'branch_code': '228', 
            'account_type': '普通預金', 
            'account': '3084648', 
            'name': 'リードバンク（ド', 
            'amount': '853305', 
            'effective_from': '2025年6月3日 0時', 
            'effective_to': '2025年8月4日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '2024年10月21日', 
            'notes': '', 
            'branch_code_jpb': '12250',
            'account_jpb': '30846481',
            'name_alias': 'リードバンク 合同会社',
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            'referer': '0'
        }
        assert result[0] == expected

        # 青木信用金庫ケースの確認
        expected = {
            'uid': '3625850bd7ba8c3e442eb6bded4ac8cb41d1466450eacb5e7af1620052b1ae74',
            'seq_no': '2',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': '青木信用金庫', 
            'branch_name': '越谷支店', 
            'branch_code': '014', 
            'account_type': '普通預金', 
            'account': '5032277', 
            'name': 'カ）パレット', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            'referer': '0'
        }
        assert result[1] == expected

        # 京葉銀行ケースの確認
        expected = {
            'uid': '2b084bca282fb34a800782b38825d63c5cdd75e5cecb3bc4a2c124be949e8030',
            'seq_no': '3',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': '京葉銀行', 
            'branch_name': '鎌取支店', 
            'branch_code': '418', 
            'account_type': '普通預金', 
            'account': '5569011', 
            'name': 'ド）シュガーラッシュ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            'referer': '0'
        }
        assert result[2] == expected

@pytest.fixture
def k_pubstype_01_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_01_detail_2(k_pubstype_01_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2506-0001-0894",
            "pn": "375331",
            "p_id": "03",
            "re": "0",
            "referer": '1'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        
        # みずほ銀行（外国人）ケースの確認
        expected = {
            'uid': 'a3d32ea5fb85016e88669290aefb562e8bb907006340a0894c6515d755409996',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '山形支店', 
            'branch_code': '728', 
            'account_type': '普通預金', 
            'account': '3056028', 
            'name': 'ＰＨＡＭ ＶＡＮ ＭＡＮＨ （フアン ヴアン マイン）', 
            'amount': '2599', 
            'effective_from': '2025年6月17日 0時', 
            'effective_to': '2025年8月18日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '2024年08月頃', 
            'suspend_date': '2024年8月16日', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2506-0001-0894', 
            'pn': '375331', 
            'p_id': '03', 
            're': '0', 
            'referer': '1'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_04_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_04_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_04_detail_1(k_pubstype_04_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_04_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_04_detail.php",
            "no": "2503-9900-0475",
            "pn": "368470",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '9d0f73c03297297403fbe423109ceabb01972a88899db5a6aebdb597d8bb0463',
            'seq_no': '1',
            'role': '対象預金口座等に係る',
            'bank_name': 'ゆうちょ銀行',
            'branch_name': '五一八',
            'branch_code': '518',
            'account_type': '普通預金',
            'account': '6211644', 
            'name': 'フャン ティ カイン リー', 
            'amount': '602827', 
            'notice_date': '2025年5月1日',
            'notes': '法第六条第一項（権利行使の届出等あり）',
            'branch_code_jpb': '15150',
            'account_jpb': '62116441',
            'name_alias': 'ＰＨＡＮ ＴＨＩ ＫＨＡＮＨ ＬＹ',
            "form": "k_pubstype_04_detail.php",
            "no": "2503-9900-0475",
            "pn": "368470",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_04_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_04_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_04_detail_2(k_pubstype_04_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_04_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_04_detail.php",
            "no": "2507-0310-0051",
            "pn": "372840",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        
        # ＧＭＯあおぞらネット銀行ケースの確認
        expected = {
            'uid': '72dbc29dee7f3293fdb6722e71c72a14bd8f6a0ad255a90708a4c57e9fc72aa2',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ＧＭＯあおぞらネット銀行', 
            'branch_name': 'フリー支店', 
            'branch_code': '125', 
            'account_type': '普通預金', 
            'account': '1121426', 
            'name': 'カ）フアイナンシヤルラグジユアリ－', 
            'amount': '8676', 
            'notice_date': '2025年7月1日',
            'notes': '法第六条第一項（権利行使の届出等あり）',
            "form": "k_pubstype_04_detail.php",
            "no": "2507-0310-0051",
            "pn": "372840",
            "p_id": "05",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_05_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_05_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_05_detail_1(k_pubstype_05_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_05_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_05_detail.php",
            "no": "2503-9900-0011",
            "pn": "373302",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # みずほ銀行ケースの確認
        expected = {
            'uid': 'e103b83c7b00c5dadc4f2107b5d99a6f20c9e91fb45c46452959d6da141eb8aa',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'name': 'ＢＵＩ ＶＡＮ ＢＩＮＨ（ブイ ウ゛ァン ビン）', 
            'amount': '773', 
            'notice_date': '2025年5月1日',
            'delete_date': '2025年7月1日',
            'branch_code_jpb': '19730',
            'account_jpb': '16099061',
            "form": "k_pubstype_05_detail.php",
            "no": "2503-9900-0011",
            "pn": "373302",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_05_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_05_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_05_detail_2(k_pubstype_05_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_05_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_05_detail.php",
            "no": "2502-0001-0034",
            "pn": "371209",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # みずほ銀行ケースの確認
        expected = {
            'uid': '019243fefd94ec3ae418cbd914602f01c34be7b580461af61671b512a432c17b',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '春日部支店', 
            'branch_code': '223', 
            'account_type': '普通預金', 
            'account': '3075321', 
            'name': 'ＰＲＥＳＥＮＴＡＣＩＯＮ ＡＬＩＣＥ ＶＩＣＴＯＲＩＡ （プレセンタシオン アリス ヴイクトリア）', 
            'amount': '151797', 
            'notice_date': '2025年4月16日',
            'delete_date': '2025年6月16日',
            "form": "k_pubstype_05_detail.php",
            "no": "2502-0001-0034",
            "pn": "371209",
            "p_id": "07",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_07_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_07_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_07_detail_1(k_pubstype_07_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_07_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 2

        # 三菱ＵＦＪ銀行ケースの確認
        expected = {
            'uid': 'dafcd7bb0fc75ccfc2dc1789b37ae5dc7c16ec1ce77a07f5611e6490e1b169b0',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': '三菱ＵＦＪ銀行', 
            'branch_name': '町田支店', 
            'branch_code': '228', 
            'account_type': '普通預金', 
            'account': '2549964', 
            'name': 'グエン ダン ビン', 
            'amount': '22004', 
            'effective_from': '2025年7月17日 0時', 
            'effective_to': '2025年10月15日 15時', 
            'effective_method': '被害回復分配金支払申請書を店頭に提出又は郵送（詳細は照会先へご連絡下さい）', 
            'payment_period': '2024年5月頃', 
            'suspend_date': '2025年7月1日', 
            'reason': 'オレオレ詐欺',
            'notes': '', 
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

        # 資金の移転元となった預金口座等に係る
        expected = {
            'uid': '5066ec5a469825b267de18c72c4ccdfd5be8c86de236eead63e916a6791c3650',
            'seq_no': '2',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '柏支店', 
            'branch_code': '329', 
            'account_type': '普通預金', 
            'account': '4157068', 
            'name': 'ＥＢＡＲＤＡＬＯＺＡ ＶＥＲＥＧＩＬＩＯ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '2024年5月頃', 
            'suspend_date': '', 
            'reason': 'オレオレ詐欺',
            'notes': '', 
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "referer": '0'
        }
        assert result[1] == expected

@pytest.fixture
def k_pubstype_09_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_09_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_09_detail_1(k_pubstype_09_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_09_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_09_detail.php",
            "no": "2411-0038-0042",
            "pn": "370345",
            "p_id": "12",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # 住信ＳＢＩネット銀行ケースの確認
        expected = {
            'uid': '3f4a9d90f23dd9d8e6b30c1bf2e9d32c7db982fcb5e03f375fe309b24a600e18',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': '住信ＳＢＩネット銀行', 
            'branch_name': '法人第一支店', 
            'branch_code': '106', 
            'account_type': '普通預金', 
            'account': '2088276', 
            'name': 'ド） エース', 
            'amount': '237019', 
            'notes': '', 
            "form": "k_pubstype_09_detail.php",
            "no": "2411-0038-0042",
            "pn": "370345",
            "p_id": "12",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_10_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_10_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_10_detail_1(k_pubstype_10_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_10_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2415-9900-0114",
            "pn": "371720",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '8c472ace1eba2338a7cf215e6d5eadb4142b0893bfce1249ab5b48a264c3edb6',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'name': 'ＴＲＡＮ ＶＡＮ ＣＡＮＨ（チャン ウ゛ァン カイン）', 
            'amount': '20153', 
            'notice_date': '2025年1月16日',
            'branch_code_jpb': '10330',
            'account_jpb': '89857121',
            "form": "k_pubstype_10_detail.php",
            "no": "2415-9900-0114",
            "pn": "371720",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_10_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_10_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_10_detail_2(k_pubstype_10_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_10_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2412-0001-0028",
            "pn": "369725",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '0989e2baf2b5504768a7c9d68de0031febc48891043b1176a31eafc6bb437ce9',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '赤羽支店', 
            'branch_code': '203', 
            'account_type': '普通預金', 
            'account': '3118190', 
            'name': 'ＮＧＵＹＥＮ ＴＨＩ ＨＯＡＩ ＮＨＩＥＮ （グエン テイ ホアイ ニエン）', 
            'amount': '450709', 
            'notice_date': '2024年12月2日',
            "form": "k_pubstype_10_detail.php",
            "no": "2412-0001-0028",
            "pn": "369725",
            "p_id": "11",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected