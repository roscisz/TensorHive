class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    roles = db.relationship("RoleModel", backref="user")

    def __repr__(self):
        return f'<User ....>'

    # TODO created, updated timestamps, role, etc.

    @jwt.user_claims_loader
    def add_claims_to_access_token(user):
        id = UserModel.query.filter_by(username=user).first().id
        all_roles = RoleModel.query.filter_by(user_id=id).all()

        def as_json(x):
            return {
                'role': x.name,
            }

        users_list = list(map(lambda role: as_json(role), all_roles))
        return {'roles': users_list}
        #roles = RoleModel.query.all.filter_by(user_id=user.id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        all_users = UserModel.query.all()

        def as_json(x):
            return {
                #FIXME delete id
                #'id': x.id,
                'username': x.username,
                'password': x.password
            }

        users_list = list(map(lambda user: as_json(user), all_users))
        return {'users': users_list}

    @classmethod
    def get_count(cls):
        count_q = self.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

        users_list = list(map(lambda user: as_json(user), all_users))
        return {'users': users_list}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} user(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Deleting all users operation failed'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)