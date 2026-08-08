from libcore_hng.core.base_app_exception import AppBaseException
from libcore_hng.exceptions.config_exception import ConfigurationException

class TestConfigurationError:

    def test_init_with_string_message(self):

        msg = "Configuration load error: missing 'api_key' in config.yml"
        err = ConfigurationException(msg)

        # 検証
        assert isinstance(err, AppBaseException)
        assert err.exc_type is None
        assert err.exc_value == msg
        assert "No exception captured" not in str(err)
        assert msg in str(err)

    def test_init_with_exception_object(self):

        cause_exc = FileNotFoundError("config.json not found")
        err = ConfigurationException(cause_exc)

        # 検証
        assert err.exc_type == FileNotFoundError
        assert err.exc_value == cause_exc
        assert "FileNotFoundError" in str(err)
        assert "config.json not found" in str(err)

    def test_raise_and_catch_fstring_formatting(self):

        config_path = "config/settings.json"

        try:
            try:
                raise ValueError("Invalid JSON format at line 10")
            except ValueError as inner_e:
                raise ConfigurationException(
                    f"Failed to parse config file '{config_path}': {inner_e}"
                ) from inner_e
        except Exception as e:
            error_str = f"Config Load Error: {e}"

            # 検証
            assert "No exception captured" not in error_str
            assert "Failed to parse config file 'config/settings.json': Invalid JSON format at line 10" in error_str
            assert e.exc_uuid is not None

    def test_default_init_without_args(self):

        err = ConfigurationException()

        # 検証
        assert err.exc_type is None
        assert err.exc_value is None
        assert "No exception captured." in str(err)