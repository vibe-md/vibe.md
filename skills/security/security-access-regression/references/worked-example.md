# Worked example: the empty-list trap

Illustrative pseudocode, not a drop-in framework adapter. Adapt it to the project's existing client, fixtures and assertions. All data is synthetic and in-process.

```python
def test_owner_list_preserves_allowed_row(client, alice, alice_doc, bob_doc):
    response = client.as_user(alice).get('/documents')
    assert response.status_code == 200
    ids = {item['id'] for item in response.json()['items']}
    assert alice_doc.id in ids  # proves fixture and allowed path work
    assert bob_doc.id not in ids  # proves this forbidden fixture was filtered


def test_denied_update_has_no_effect(client, alice, bob_doc, fake_jobs):
    before = snapshot(bob_doc)
    jobs_before = list(fake_jobs.items)
    response = client.as_user(alice).patch(
        f'/documents/{bob_doc.id}', json={'title': 'SYNTHETIC-CHANGED'}
    )
    assert response.status_code == 404  # this example's documented policy
    assert snapshot(reload(bob_doc)) == before
    assert fake_jobs.items == jobs_before
```

Three implementations distinguish whether the list test is meaningful:

| Implementation | Expected test outcome |
| --- | --- |
| Owner-scoped query returning Alice's document only | Pass |
| Query returning every document | Fail because Bob appears |
| Query returning an empty list for everybody | Fail because Alice disappears |

For the write test, returning 404 *after* changing Bob's document or enqueueing a job must fail. A status-only assertion misses that regression.

In a disposable source copy, temporarily bypass the owner filter, then temporarily replace its result with an empty list. Record the failed assertions. Do not change the policy, weaken expectations, or leave the mutation in the delivered diff just to get a green run.
