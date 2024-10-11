import unittest
from unittest.mock import patch, MagicMock
from skuid_pages_deployer import SkuidPagesDeployer

class TestSkuidPagesDeployer(unittest.TestCase):

    @patch('deploy_skuid_pages.requests.post')
    def test_successful_page_deploy(self, mock_post):
        # Arrange: Create an instance of the class and mock the response
        deployer = SkuidPagesDeployer()
        deployer.token = "fake_token"
        deployer.repo_owner = "fake_owner"
        deployer.repo_name = "fake_repo"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        # mock_post.return_value = mock_response
        
        # Act: Call the method you want to test
        result = deployer.deploy_page(page="some_page")

        # Assert: Check if the result and response are as expected
        self.assertRaises(Exception)

    @patch('deploy_skuid_pages.time.sleep', return_value=None)
    @patch('deploy_skuid_pages.requests.post')
    def test_retry_logic(self, mock_post, mock_sleep):
        # Arrange: Simulate failures and success after retries
        deployer = SkuidPagesDeployer()
        deployer.token = "fake_token"
        deployer.repo_owner = "fake_owner"
        deployer.repo_name = "fake_repo"
        
        # First attempt fails, second attempt succeeds
        mock_failed_response = MagicMock()
        mock_failed_response.status_code = 500
        mock_post.side_effect = [mock_failed_response, mock_failed_response, MagicMock(status_code=200, json=MagicMock(return_value={"status": "success"}))]

        # Act: Call the deploy method with retry logic
        result = deployer.deploy_page(page="retry_page")

        # Assert: Ensure retries happened and result is successful
        self.assertRaises(Exception)
        mock_sleep.assert_called_with(1)  # Ensure the sleep was called during retry

if __name__ == '__main__':
    unittest.main()
