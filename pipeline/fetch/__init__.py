"""
Network fetchers — run these LOCALLY (with network access and any required API
keys) to produce the raw CSV files under data/raw/<source>/ that the ingesters
read. The core pipeline never touches the network; fetching is an explicit,
separate step so pipeline runs stay offline and deterministic.

  python3 -m pipeline.fetch.opensecrets --help
  python3 -m pipeline.fetch.propublica_nonprofits --help
"""
