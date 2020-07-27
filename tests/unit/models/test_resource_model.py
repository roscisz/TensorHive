from tensorhive.models.Resource import Resource


def test_resource_creation(tables):
    new_resource = Resource(id="34943e60-0acd-4c31-b96e-02f88cc156f3")
    new_resource.save()

    assert Resource.get(new_resource.id) is not None
