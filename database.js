const {Client} = require('pg')

const client = new Client({
host: "localhost",
user: "postgres",
port: 5432,
password: "gaurav76",
database: "doc_gov_id"})

client.connect();

client.query('SELECT * FROM "reg_gov_id_table"', (err, res) => {


    if (!err)
        console.log(res.rows);

    else {
        console.log(err.message);

    }
    client.end;
})