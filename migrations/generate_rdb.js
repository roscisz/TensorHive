#!/usr/bin/node

// This script's purpose is to generate a database diagram based on provided SQLite database.
// It should be invoked like this: node generate_rdb.js <path_to_sqlite_database>
// It requires sqleton and sqlite3 modules installed to function.
// It is invoked automatically (with user's confirmation) after migrating database using
// `alembic upgrade head` command.
// The resulting image is saved in the `images` directory as `dbdiagram.svg`.

const sqleton = require('sqleton');
const sqlite3 = require('sqlite3');
const fs = require('fs');
const db_url = process.argv[2].replace('sqlite:///', '');


let db = new sqlite3.Database(db_url);
let writeStream = fs.createWriteStream(__dirname + '/../images/dbdiagram.svg');
sqleton(db, writeStream, {'title': 'TensorHive'})
    .then(() => { db.close() })
    .then(() => { writeStream.end() });
