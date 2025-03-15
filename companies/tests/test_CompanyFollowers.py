from django.core.exceptions import ValidationError
from django.test import TestCase
from companies.models import CompanyProfile, CompanyFollowers

class CompanyFollowersModelTest(TestCase):

    def setUp(self):
        """Create companies for testing."""
        self.enterprise = CompanyProfile.objects.create(company_name="Big Corp", type="enterprise")
        self.investor = CompanyProfile.objects.create(company_name="VC Firm", type="enterprise")
        self.startup = CompanyProfile.objects.create(company_name="Tech Startup", type="startup")
        self.nonprofit = CompanyProfile.objects.create(company_name="Helping Hands", type="nonprofit")

    def test_valid_investor_startup_relation(self):
        """Check that an investor (enterprise) can invest in a startup."""
        relation = CompanyFollowers.objects.create(investor=self.enterprise, startup=self.startup)
        self.assertEqual(relation.investor, self.enterprise)
        self.assertEqual(relation.startup, self.startup)

    def test_invalid_investor_type(self):
        """Ensure that a startup or nonprofit cannot be an investor."""
        with self.assertRaises(ValidationError):
            invalid_relation = CompanyFollowers(investor=self.startup, startup=self.enterprise)
            invalid_relation.full_clean()  # Trigger validation before saving

        with self.assertRaises(ValidationError):
            invalid_relation = CompanyFollowers(investor=self.nonprofit, startup=self.startup)
            invalid_relation.full_clean()

    def test_invalid_startup_type(self):
        """Ensure that an investor cannot invest in a non-startup company."""
        with self.assertRaises(ValidationError):
            invalid_relation = CompanyFollowers(investor=self.investor, startup=self.enterprise)
            invalid_relation.full_clean()

    def test_unique_relation(self):
        """Ensure that duplicate investment relations cannot be created."""
        CompanyFollowers.objects.create(investor=self.enterprise, startup=self.startup)
        with self.assertRaises(Exception):  # Django will raise an IntegrityError
            CompanyFollowers.objects.create(investor=self.enterprise, startup=self.startup)
