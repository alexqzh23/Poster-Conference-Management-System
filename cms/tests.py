from django.test import TestCase
from cms.models_committee import CommitteeMember


class CommitteeMemberTestCase(TestCase):
    def setUp(self):
        # nothing should run before test method now
        pass

    def test_ip_in_subnet(self):
        # boundary test
        member = CommitteeMember()
        self.assertTrue(member.check_ip("172.16.0.0"))
        self.assertTrue(member.check_ip("172.24.0.0"))
        self.assertTrue(member.check_ip("172.31.255.255"))

    def test_ip_is_invalid(self):
        # boundary test & equivalence class test
        member = CommitteeMember()
        self.assertFalse(member.check_ip("172.15.255.255"))
        self.assertFalse(member.check_ip("172.32.0.0"))
        self.assertFalse(member.check_ip("a.b.c.d"))
        self.assertFalse(member.check_ip("172"))
        self.assertFalse(member.check_ip("172.16"))
        self.assertFalse(member.check_ip("172.16.0"))
        with self.assertRaises(ValueError):
            member.check_ip("172.16.0.0.0")
        with self.assertRaises(ValueError):
            member.check_ip("172.15.255.256")

    def test_ID_is_valid(self):
        # due to the randomness of id generation, we need a large number of test cases to ensure its validity
        i = 0
        while i < 10000:
            i += 1
            member = CommitteeMember()
            # each bit of ID consists of only numbers or letters
            self.assertTrue(member.get_user_id().isalnum())
            # ID must have exactly 8 digits
            self.assertEqual(len(member.get_user_id()), 8)

    def test_pwd_is_valid(self):
        # Due to the randomness of password generation, we need a large number of test cases to ensure its validity
        i = 0
        while i < 10000:
            i += 1
            member = CommitteeMember()
            # each bit of password consists of only numbers or letters
            self.assertTrue(member.get_pwd().isalnum())
            # password must have exactly 10 digits
            self.assertEqual(len(member.get_pwd()), 10)
