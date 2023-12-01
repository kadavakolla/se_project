from flask import Flask, request, jsonify
from collections import Counter
import mysql.connector

app = Flask(__name__)

class Patient:
    def __init__(self,patient_id, name, age,medical_condition, blood_type, antibody, needed_organ, organ_size, waited_time, priority_score):
        self.patient_id=patient_id
        self.name = name
        self.age = age
        self.medical_condition = medical_condition
        self.blood_type = blood_type
        self.antibody = antibody
        self.needed_organ = needed_organ
        self.organ_size = organ_size
        self.waited_time = waited_time
        self.priority_score = priority_score
        

    def __hash__(self):
        return hash(self.patient_id)

    def __eq__(self, other):
        return self.patient_id == other.patient_id


class Organ:
    def __init__(self, donor_id, organ,blood_type, organ_size,antibody):
        self.donor_id = donor_id
        self.organ = organ
        self.blood_type = blood_type
        self.organ_size = organ_size
        self.antibody = antibody


# MySQL database setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'helloworld',
    'database': 'odms'
}

def create_table():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            donor_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INT NOT NULL,
            organ VARCHAR(20) NOT NULL,
            blood_type VARCHAR(5) NOT NULL,
            organ_size FLOAT(2,1) NOT NULL,
            antibody VARCHAR(10) NOT NULL
        ) AUTO_INCREMENT = 1000
    ''')

    # Creating table 'patients'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INT NOT NULL,
            medical_condition INT NOT NULL,
            blood_type VARCHAR(5) NOT NULL,
            antibody VARCHAR(10) NOT NULL,
            needed_organ VARCHAR(10) NOT NULL,
            organ_size FLOAT(2,1) NOT NULL,
            waited_time INT NOT NULL,
            priority_score INT NOT NULL
        ) AUTO_INCREMENT = 1
    ''')

    # Creating table 'organs'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organs (
            donor_id INT,
            organ VARCHAR(20) NOT NULL,
            blood_type VARCHAR(5) NOT NULL,
            organ_size FLOAT(2,1) NOT NULL,
            antibody VARCHAR(10) NOT NULL,
            FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS after_donor_insert
        AFTER INSERT ON donors
        FOR EACH ROW
        BEGIN
            INSERT INTO organs (donor_id, organ, blood_type, organ_size,antibody)
            VALUES (NEW.donor_id, NEW.organ, NEW.blood_type, NEW.organ_size,NEW.antibody);
        END;
    ''')

    conn.commit()
    conn.close()

@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        name = request.json['name']
        age = request.json['age']
        medical_condition = request.json['medical_condition']
        blood_type = request.json['blood_type']
        antibody = request.json['antibody']
        needed_organ = request.json['needed_organ']
        organ_size = request.json['organ_size']
        waited_time = request.json['waited_time']
        priority_score = request.json['priority_score']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO patients (name, age, medical_condition, blood_type, antibody, needed_organ, organ_size,waited_time, priority_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, age, medical_condition,blood_type,antibody,needed_organ,organ_size,waited_time,priority_score))
        conn.commit()
        conn.close()

        return jsonify({'message': 'patient added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/add_donor', methods=['POST'])
def add_donor():
    try:
        name = request.json['name']
        age = request.json['age']
        organ = request.json['organ']
        organ_size = request.json['organ_size']
        blood_type = request.json['blood_type']
        antibody = request.json['antibody']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO donors (name, age, organ, organ_size,blood_type, antibody) VALUES (%s, %s, %s, %s, %s, %s)', (name, age,organ,organ_size,blood_type,antibody))
        conn.commit()
        conn.close()

        return jsonify({'message': 'donor added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/fetch_patients()', methods=['GET'])
def fetch_patients():
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients')
        patients_data = cursor.fetchall()
        conn.close()
        p_arr=[]
        for p in patients_data:
            p_arr.append(Patient(*p))

        return p_arr


def fetch_available_organ_for_patient(patient):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organs WHERE organ = %s AND blood_type = %s AND organ_size = %s", (patient.needed_organ,patient.blood_type,patient.organ_size))
    organ_data = cursor.fetchone()
    conn.close()

    if organ_data:
        return Organ(*organ_data)
    else:
        return None

def calculate_priority_medical_urgency(patients):
    for patient in patients:
        if patient.antibody == "low":
            patient.medical_condition += 5
        if patient.antibody == "fair":
            patient.medical_condition += 2
        if patient.antibody == "good":
            patient.medical_condition += 0
        if patient.age >= 80:
            patient.medical_condition += 8
        if patient.age >= 50 and patient.age < 80 :
            patient.medical_condition += 5
        if patient.age >= 30 and patient.age < 50 :
            patient.medical_condition += 3
        if patient.age < 30:
            patient.medical_condition += 0
        patient.priority_score += patient.medical_condition
    return patients

def check_matching_criteria(patients):
    for patient in patients:
        available_organ = fetch_available_organ_for_patient(patient)
        if available_organ:
            patient.priority_score += 10

def consider_time_on_waiting_list(patients):
    for patient in patients:
        patient.priority_score += (patient.waited_time)//10
    return patients


def calc_priority(patients):
    calculate_priority_medical_urgency(patients)
    check_matching_criteria(patients)
    consider_time_on_waiting_list(patients)

@app.route('/display_list', methods=['GET'])
def display_list():
    patients = fetch_patients()
    calc_priority(patients)
    priority_scores = Counter({patient: patient.priority_score for patient in patients})
    messages=[]
    for patient, score in priority_scores.most_common():
        # jsonify({'message': f"Patient: {patient.name}, Priority Score: {score}"}), 200
        messages.append({'message': f"Patient_id: {patient.patient_id}, Patient_name: {patient.name}, Requested_organ: {patient.needed_organ}, Organ_size: {patient.organ_size}, Medical_condition: {patient.medical_condition}, Waited_time: {patient.waited_time}, Priority Score: {score}"})
    return jsonify(messages), 200


if __name__ == '__main__':
    create_table()
    app.run(debug=True)