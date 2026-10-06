from tools.release_gate import resolve_matrix

def test_nonexistent_required_reference_blocks_release():
    matrix={
        "scenarios":[{
            "id":"missing-required",
            "required":True,
            "coverage_scope":"component",
            "tests":["suite::test_does_not_exist"],
            "expected":"must resolve",
        }]
    }
    cases=[
        {"suite":"suite","repetition":1,"name":"test_real","test_id":"suite::test_real","status":"passed","reason":"","evidence_path":"run-1/suite.xml","classname":"x"},
        {"suite":"suite","repetition":2,"name":"test_real","test_id":"suite::test_real","status":"passed","reason":"","evidence_path":"run-2/suite.xml","classname":"x"},
    ]
    ok,resolved=resolve_matrix(matrix,cases)
    assert ok is False
    assert resolved[0]["status"]=="missing"
    assert len(resolved[0]["missing"])==2
