pushd ..

  if [ $# -ne 1 ]; then
    echo "No test config file provided!"
    exit 1
  fi

  if [ -d ".venv" ]; then
    source .venv/bin/activate
    python3 main.py -config_file="$1"
  else
    echo "No Virtual environment defined (run ./setup.sh)"
  fi
popd || exit