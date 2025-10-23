pushd ..
  if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip3 install -r requirements.txt
    python3 main.py
  else
    echo "No Virtual environment defined (run ./setup.sh)"
  fi
popd || exit