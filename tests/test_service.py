import pytest
from ledgerlens.service import analyze
from ledgerlens.schemas import AnalysisRequest
from ledgerlens.demo import demo_request
from helpers import facts,query


def test_analysis_layers_provenance_and_conclusions():
 request=AnalysisRequest(companyfacts=facts(),query=query())
 result=analyze(request)
 assert result['metrics']['revenue_yoy']==pytest.approx(.25)
 assert result['connections']['cash_bridge']['residual']==0
 assert result['metadata']['input_sha256']==analyze(request)['metadata']['input_sha256']
 assert result['data_label']=='USER PROVIDED DATA'
 assert result['interpretation'][0]['kind']=='calculated_interpretation'
 assert any('cash' in x['title'].lower() for x in result['interpretation'])
 assert result['evidence']['facts']['revenue']['value']==1000


def test_demo_is_labeled_and_schema_valid():
 request=demo_request();result=analyze(request)
 assert result['data_label']=='DEMO DATA'
 assert result['metadata']['entity'].startswith('DEMO DATA')
 assert result['metrics']['balance_sheet_residual']==0
