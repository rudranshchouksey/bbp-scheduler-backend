from app.models import Equipment, Batch


def _seed(session):
    eq = Equipment(name="15L"); session.add(eq); session.commit(); session.refresh(eq)
    b = Batch(name="Test-Batch"); session.add(b); session.commit(); session.refresh(b)
    return eq, b


def test_create_unit_op(client, session):
    eq, b = _seed(session)
    res = client.post("/api/unit_operations", json={
        "name": "Seed", "status": "draft",
        "start": "2026-03-01T00:00:00",
        "end": "2026-03-03T00:00:00",
        "batch_id": b.id, "equipment_id": eq.id,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Seed"
    assert data["color"] == "#6366f1"   # auto-assigned


def test_update_unit_op_status(client, session):
    eq, b = _seed(session)
    create = client.post("/api/unit_operations", json={
        "name": "Seed", "status": "draft",
        "start": "2026-03-01T00:00:00", "end": "2026-03-03T00:00:00",
        "batch_id": b.id, "equipment_id": eq.id,
    })
    op_id = create.json()["id"]
    res = client.put(f"/api/unit_operations/{op_id}", json={"status": "confirmed"})
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"


def test_delete_unit_op(client, session):
    eq, b = _seed(session)
    create = client.post("/api/unit_operations", json={
        "name": "Seed", "status": "draft",
        "start": "2026-03-01T00:00:00", "end": "2026-03-03T00:00:00",
        "batch_id": b.id, "equipment_id": eq.id,
    })
    op_id = create.json()["id"]
    assert client.delete(f"/api/unit_operations/{op_id}").status_code == 204


def test_update_nonexistent_returns_404(client, session):
    res = client.put("/api/unit_operations/9999", json={"status": "confirmed"})
    assert res.status_code == 404


def test_schedule_returns_violations(client, session):
    eq = Equipment(name="20L"); session.add(eq); session.commit(); session.refresh(eq)
    b1 = Batch(name="B1"); session.add(b1); session.commit(); session.refresh(b1)
    b2 = Batch(name="B2"); session.add(b2); session.commit(); session.refresh(b2)

    client.post("/api/unit_operations", json={
        "name": "Seed", "status": "draft",
        "start": "2026-03-01T00:00:00", "end": "2026-03-05T00:00:00",
        "batch_id": b1.id, "equipment_id": eq.id,
    })
    client.post("/api/unit_operations", json={
        "name": "Bioreactor", "status": "draft",
        "start": "2026-03-03T00:00:00", "end": "2026-03-08T00:00:00",
        "batch_id": b2.id, "equipment_id": eq.id,
    })
    res = client.get("/api/schedule?start_date=2026-03-01T00:00:00&end_date=2026-03-31T00:00:00")
    assert res.status_code == 200
    assert len(res.json()["violations"]) > 0