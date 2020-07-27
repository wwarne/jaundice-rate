import pytest
from settings import load_settings, Config

@pytest.mark.parametrize('cmd_param, attribute_name, result', [
    ('--port=9999', 'port', 9999),
    ('--request_timeout=10.5', 'request_timeout', 10.5),
    ('--process_timeout=5.0', 'process_timeout', 5.0),
    ('--urls_limit=100', 'urls_limit', 100),
])
def test_process_cmd_arguments(cmd_param, attribute_name, result):
    config = load_settings(cmd_params=[cmd_param])
    assert getattr(config, attribute_name) == result


@pytest.mark.parametrize('env_name, env_value, attribute_name, result', [
    ('NEWS_PORT', '9999', 'port', 9999),
    ('NEWS_REQUEST_TIMEOUT', '10.5', 'request_timeout', 10.5),
    ('NEWS_PROCESS_TIMEOUT', '5.0', 'process_timeout', 5.0),
    ('NEWS_URL_LIMIT', '100', 'urls_limit', 100),
])
def test_reading_env_variables(monkeypatch, env_name, env_value, attribute_name, result):
    monkeypatch.setenv(env_name, env_value)
    config = load_settings(cmd_params=[])
    assert getattr(config, attribute_name) == result


def test_config_key_names():
    config = Config()
    assert set(config.__dict__.keys()) == {
        'port',
        'request_timeout',
        'process_timeout',
        'urls_limit',
    }
