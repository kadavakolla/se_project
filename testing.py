import unittest
from unittest.mock import MagicMock, patch
from app import *


class TestAppFunctions(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_fetch_patients(self):
        # Test fetch_patients function
        # Mocking database connection and cursor
        with patch('app.mysql.connector.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_connect.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [(1, 'John', 40, 1, 'AB+', 'low', 'kidney', 3.0, 50, 60)]
            
            patients = fetch_patients()
            self.assertEqual(len(patients), 1)
            
    def test_fetch_available_organ_for_patient(self):
        # Test fetch_available_organ_for_patient function
        # Mocking database connection and cursor
        with patch('app.mysql.connector.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_connect.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1001, 'kidney', 'AB+', 3.0, 'low')

            test_patient = Patient(1, 'John', 40, 1, 'AB+', 'low', 'kidney', 3.0, 50, 60)
            organ = fetch_available_organ_for_patient(test_patient)
            self.assertIsNotNone(organ)

    def test_calculate_priority_medical_urgency(self):
        # Test calculate_priority_medical_urgency function
        test_patients = [
            Patient(1, 'John', 40, 0, 'AB+', 'low', 'kidney', 3.0, 50, 0),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'liver', 3.0, 100, 0),
        ]

        calculate_priority_medical_urgency(test_patients)
        expt = [
            Patient(1, 'John', 40, 0, 'AB+', 'low', 'kidney', 3.0, 50, 0+5+3),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'liver', 3.0, 100, 0+2+5),
        ]
        self.assertEqual(expt[0].priority_score, test_patients[0].priority_score)
        self.assertEqual(expt[1].priority_score, test_patients[1].priority_score)

    def test_check_matching_criteria(self):
        # Test check_matching_criteria function
        test_patients = [
            Patient(1, 'John', 40, 0, 'A+', 'low', 'kidney', 3.5, 50, 0),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'kidney', 3.0, 100, 0),
        ]

        check_matching_criteria(test_patients)

        expt = [
            Patient(1, 'John', 40, 0, 'A+', 'low', 'kidney', 3.5, 50, 0+10),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'kidney', 3.0, 100, 0),
        ]

    def test_consider_time_on_waiting_list(self):
        # Test consider_time_on_waiting_list function
        test_patients = [
            Patient(1, 'John', 40, 0, 'AB+', 'low', 'kidney', 3.0, 50, 0),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'liver', 3.0, 100, 0),
        ]

        consider_time_on_waiting_list(test_patients)
        
        expt = [
            Patient(1, 'John', 40, 0, 'AB+', 'low', 'kidney', 3.0, 50, 0+5),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'liver', 3.0, 100, 0+10),
        ]
        self.assertEqual(expt[0].priority_score, test_patients[0].priority_score)
        self.assertEqual(expt[1].priority_score, test_patients[1].priority_score)

    def test_calc_priority(self):
        # Test calc_priority function
        test_patients = [
            Patient(1, 'John', 40, 0, 'A+', 'low', 'kidney', 3.5, 50, 0),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'kidney', 3.0, 100, 0),
        ]

        calc_priority(test_patients)

        expt = [
            Patient(1, 'John', 40, 0, 'A+', 'low', 'kidney', 3.5, 50, 0+5+3+5+10),
            Patient(2, 'Alice', 56, 0, 'B+', 'fair', 'kidney', 3.0, 100, 0+2+5+10),
        ]

        self.assertEqual(expt[0].priority_score, test_patients[0].priority_score)
        self.assertEqual(expt[1].priority_score, test_patients[1].priority_score)

if __name__ == '__main__':
    unittest.main()
