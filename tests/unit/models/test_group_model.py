from tensorhive.models.Group import Group


def test_group_creation(tables):
    new_group = Group(name='test').save()
    assert new_group.id is not None


def test_adding_user_to_a_group(tables, new_user, new_group):
    new_user.save()
    new_group.add_user(new_user)

    assert new_user in new_group.users
    assert new_group in new_user.groups


def test_removing_user_from_a_group(tables, new_group_with_member):
    user = new_group_with_member.users[0]
    new_group_with_member.remove_user(user)

    assert user not in new_group_with_member.users
    assert new_group_with_member not in user.groups
