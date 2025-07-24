import pytest
from sagikoza import core
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

@pytest.fixture
def sel_pubs_html():
    # テスト用HTMLを読み込む
    with open("test/pages/sel_pubs.php", encoding="utf-8") as f:
        return f.read()

def test_sel_pubs(sel_pubs_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(sel_pubs_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        result = core._sel_pubs("near3")
        assert isinstance(result, list)
        assert len(result) == 195
        # 指定した辞書が含まれるかどうか
        expected = {
            'notice_round': '24年度第20回', 
            'notice_type': '権利行使の届出等',
            'notice_number': '公告（07）第043号',
            'notice_date': '令和７年４月２３日',
            'doc_id': '15362'
        }
        assert result[1] == expected
        # 指定した辞書が含まれるかどうか
        expected_without_bracket = {
            'notice_round': '25年度第03回', 
            'notice_type': '債権消滅',
            'notice_number': '公告（07）第072号',
            'notice_date': '令和７年５月１日',
            'doc_id': '15402'
        }
        assert result[100] == expected_without_bracket

def test_sel_pubs_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        result = core._sel_pubs("near3")
        assert result == []

def test_sel_pubs_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        with pytest.raises(core.FetchError):
            core._sel_pubs("near3")

@pytest.fixture
def pubs_dispatcher_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubs_dispatcher.php", encoding="utf-8") as f:
        return f.read()

def test_pubs_dispatcher(pubs_dispatcher_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubs_dispatcher_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        notice = {'doc_id': '15362'}
        result = core._pubs_dispatcher(notice)
        assert isinstance(result, list)
        assert len(result) == 8
        # 指定した辞書が含まれるかどうか
        expected = {
            'inst_code': '0310', 
            'p_id': '03', 
            'pn': '365699', 
            're': '0', 
            'params': 'inst_code=0310&p_id=03&pn=365699&re=0', 
            'doc_id': '15362'
        }
        assert result[6] == expected

def test_pubs_dispatcher_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        notice = {'doc_id': '15362'}
        result = core._pubs_dispatcher(notice)
        # リファクタリング後は空の場合エラーメッセージが返される
        assert len(result) == 1
        # 指定した辞書が含まれるかどうか
        expected = {'doc_id': '15362', 'error': 'No submit found'}
        assert result[0] == expected

def test_pubs_dispatcher_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        notice = {'doc_id': '15362'}
        with pytest.raises(core.FetchError):
            core._pubs_dispatcher(notice)

@pytest.fixture
def pubs_basic_frame_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubs_basic_frame.php", encoding="utf-8") as f:
        return f.read()

def test_pubs_basic_frame(pubs_basic_frame_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubs_basic_frame_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        submit = {'params': 'inst_code=0034&p_id=03&pn=365600&re=0'}
        result = core._pubs_basic_frame(submit)
        assert isinstance(result, list)
        assert len(result) == 44
        # 指定した辞書が含まれるかどうか
        expected = {
            'form': 'k_pubstype_01_detail.php', 
            'no': '2421-0034-0004', 
            'params': 'inst_code=0034&p_id=03&pn=365600&re=0'
        }
        assert result[3] == expected

def test_pubs_basic_frame_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        submit = {'params': 'inst_code=0034&p_id=03&pn=365600&re=0'}
        result = core._pubs_basic_frame(submit)
        expected = {
            'error': 'No subjects found for submit params=inst_code=0034&p_id=03&pn=365600&re=0', 
            'params': 'inst_code=0034&p_id=03&pn=365600&re=0'
        }
        assert result[0] == expected

def test_pubs_basic_frame_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        submit = {'params': 'inst_code=0034&p_id=03&pn=365600&re=0'}
        with pytest.raises(core.FetchError):
            core._pubs_basic_frame(submit)

@pytest.fixture
def pubstype_detail_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubstype_detail.php", encoding="utf-8") as f:
        return f.read()

def test_pubstype_detail(pubstype_detail_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubstype_detail_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 4
        # 指定した辞書が含まれるかどうか
        expected = {
            'role': '対象預金口座等に係る', 
            'bank_name': 'セブン銀行', 
            'branch_name': 'バラ支店', 
            'branch_code': '107', 
            'account_type': '普通預金', 
            'account': '2639227', 
            'name': 'ヤマダ リカ', 
            'amount': '5390030', 
            'effective_from': '2025年2月4日 0時', 
            'effective_to': '2025年4月7日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '', 
            'suspend_date': '2024年7月16日', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2421-0034-0004', 
            'pn': '365600', 
            'p_id': '0034', 
            're': '0', 
            'referer': '0'
        }
        assert result[0] == expected

@pytest.fixture
def pubstype_detail_2_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubstype_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_pubstype_detail_2(pubstype_detail_2_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubstype_detail_2_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2505-0543-0040",
            "pn": "369281",
            "p_id": "01",
            "re": "0"
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 3
        # 指定した辞書が含まれるかどうか
        expected = {
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '四〇八', 
            'branch_code': '408', 
            'account_type': '普通預金', 
            'account': '7555041', 
            'name': 'ミヤモト マサユキ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '2025年2月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-0543-0040', 
            'pn': '369281', 
            'p_id': '01', 
            're': '0',
            'branch_code_alias': '14000',
            'account_alias': '755504'
        }
        assert result[1] == expected

@pytest.fixture
def pubstype_detail_3_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubstype_detail_3.php", encoding="utf-8") as f:
        return f.read()

def test_pubstype_detail_3(pubstype_detail_3_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubstype_detail_3_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2508-0001-0020",
            "pn": "372858",
            "p_id": "01",
            "re": "0"
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        # 指定した辞書が含まれるかどうか
        expected = {
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '綾瀬支店', 
            'branch_code': '179', 
            'account_type': '普通預金', 
            'account': '3075533', 
            'name': 'ホー ミン ヴー', 
            'amount': '670', 
            'effective_from': '2025年7月17日 0時', 
            'effective_to': '2025年9月16日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '2025年01月頃', 
            'suspend_date': '2025年1月31日', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2508-0001-0020', 
            'pn': '372858', 
            'p_id': '01', 
            're': '0',
            'name_alias': 'ＨＯ ＭＩＮＨ ＶＵ'
        }
        assert result[0] == expected

@pytest.fixture
def pubstype_detail_4_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubstype_detail_4.php", encoding="utf-8") as f:
        return f.read()

def test_pubstype_detail_4(pubstype_detail_4_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubstype_detail_4_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2409-9900-0467",
            "pn": "365843",
            "p_id": "11",
            "re": "0"
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        # 指定した辞書が含まれるかどうか
        expected = {
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_code_alias': '17470', 
            'account_alias': '94921311', 
            'name': 'ツルゾノ レイ', 
            'amount': '15145', 
            'suspend_date': '2024年10月16日', 
            'form': 'k_pubstype_10_detail.php', 
            'no': '2409-9900-0467', 
            'pn': '365843', 
            'p_id': '11', 
            're': '0',
            'name_alias': '鶴園 零'
        }
        assert result[0] == expected

@pytest.fixture
def pubstype_detail_5_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubstype_detail_5.php", encoding="utf-8") as f:
        return f.read()

def test_pubstype_detail_5(pubstype_detail_5_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubstype_detail_5_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2506-0010-0010",
            "pn": "369660",
            "p_id": "01",
            "re": "0"
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        # 指定した辞書が含まれるかどうか
        expected = {
            'role': '対象預金口座等に係る', 
            'bank_name': 'りそな銀行', 
            'branch_name': '茗荷谷支店', 
            'branch_code': '461', 
            'account_type': '普通預金', 
            'account': '1331433', 
            'name': 'ミツイスミトモカイジヨウカサイホケン（カ）ダイリテン', 
            'amount': '500000', 
            'effective_from': '2025年6月17日 0時', 
            'effective_to': '2025年8月18日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '2003年～2024年10月', 
            'suspend_date': '2024年10月2日', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2506-0010-0010', 
            'pn': '369660', 
            'p_id': '01', 
            're': '0'
        }
        assert result[0] == expected

def test_pubstype_detail_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        expected = {
            'error': 'No accounts found for subject no=2421-0034-0004',
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "referer": '0'
        }
        assert result[0] == expected

def test_pubstype_detail_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "referer": '0'
        }
        with pytest.raises(core.FetchError):
            core._pubstype_detail(subject)

def test_fetch_integration():
    # 各関数の返り値をモックして統合テスト
    with patch("sagikoza.core._sel_pubs", return_value=[{"doc_id": "15362"}]):
        with patch("sagikoza.core._pubs_dispatcher", return_value=[{"params": "p", "doc_id": "15362"}]):
            with patch("sagikoza.core._pubs_basic_frame", return_value=[{"form": "f.php", "no": "n", "params": "p"}]):
                with patch("sagikoza.core._pubstype_detail", return_value=[{"account": "a", "form": "f.php", "no": "n", "params": "p"}]):
                    result = core.fetch("near3")
                    assert isinstance(result, list)
                    assert len(result) == 1
                    # ユニークIDが追加されていることを確認
                    assert "uid" in result[0]
                    assert isinstance(result[0]["uid"], str)
                    assert len(result[0]["uid"]) == 32  # MD5ハッシュの長さ
                    # 元のデータが含まれていることを確認
                    expected_fields = {"account": "a", "form": "f.php", "no": "n", "params": "p"}
                    for key, value in expected_fields.items():
                        assert result[0][key] == value

def test_fetch_empty():
    with patch("sagikoza.core._sel_pubs", return_value=[]):
        result = core.fetch("near3")
        assert result == []

@pytest.fixture
def pubs_basic_frame_pagination_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubs_basic_frame_pagination.php", encoding="utf-8") as f:
        return f.read()

def test_create_pagination_list_with_pagination(pubs_basic_frame_pagination_html):
    from sagikoza.parser.pubs_basic_frame import create_pagination_list
    soup = BeautifulSoup(pubs_basic_frame_pagination_html, "html.parser")
    result = create_pagination_list(soup)
    # 2から23までの数字のリストが返される（range(2, 24)は2から23まで）
    expected = list(range(2, 24))
    assert result == expected

def test_create_pagination_list_no_pagination(pubs_basic_frame_html):
    from sagikoza.parser.pubs_basic_frame import create_pagination_list
    soup = BeautifulSoup(pubs_basic_frame_html, "html.parser")
    result = create_pagination_list(soup)
    # ページネーションがない場合は空のリストが返される
    assert result == []