pushd ..
  if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip3 install -r requirements.txt
    python3 main.py -config_file=samples/sample_experiment_write_latency.yaml
  else
    echo "No Virtual environment defined (run ./setup.sh)"
  fi
popd || exit