  /*** @jsx React.DOM */
class OrderDashboard extends React.Component {
  constructor(props) {
    super(props)
    this.state={json_req:{num_files:0,num_orders:0}}
    this.callQuery = this.callQuery.bind(this)
  }

  componentDidMount() {
    window.componentHandler.upgradeElement(this.root);
    this.callQuery()
  }

  componentWillUnmount() {
    window.componentHandler.downgradeElements(this.root);
  }

  callQuery() {
    let request_url = '/api/order_and_file_count';
    let request = new XMLHttpRequest();
    request.onreadystatechange = (e) => {
      if (request.readyState !== 4) {
        return;
      }

      if (request.status === 200) {
        let json_req = JSON.parse(request.response)
        this.setState({json_req});
      } else {
        console.warn('error');
      }
    };
    request.open('GET', request_url);
    request.send();
  }

  render() {
    const pieresult = (this.state.json_req.num_files/this.state.json_req.num_orders) * 314;
    const circumference = '360';
    const dasharray = pieresult + ' ' + circumference;
    return <div ref={node => (this.root = node)}>
      <div className="mdl-color--white mdl-card mdl-shadow--2dp mdl-cell mdl-cell--12-col mdl-grid">
        {this.state.json_req.num_files == 0 ?
          <div className="mdl-spinner mdl-js-spinner is-active"></div> :
          <div className="mdl-grid">
            <div className="mdl-cell mdl-cell--4-col mdl-color--white">
              <svg width="200" height="200" className="piechart">
                <circle r="50" cx="100" cy="100" className="pie" style={{strokeDasharray: dasharray}}/>
              </svg>
            </div>
            <div className="mdl-cell mdl-cell--8-col align-text-right">
            <div className="blue">{this.state.json_req.num_files} orders with available files</div>
            <div>{this.state.json_req.num_orders} orders</div>
            </div>
          </div>
        }
      </div>
      <div className="mdl-color--white mdl-card mdl-shadow--2dp mdl-cell mdl-cell--12-col mdl-grid">
        <div className="mdl-cell--3-col mf-info-card mdl-card mdl-shadow--2dp">
          <div className="mdl-card__title mdl-card--expand">
            <h4>Divisions</h4>
            <h1>{this.state.json_req.division_count}</h1>
          </div>
          <div className="mdl-card__actions mdl-card--border">
          <div className="mdl-layout-spacer"></div>
          </div>
        </div>
        <div className="mdl-cell--3-col mf-info-card mdl-card mdl-shadow--2dp">
          <div className="mdl-card__title mdl-card--expand">
            <h4>Districts</h4>
            <h1>{this.state.json_req.district_count}</h1>
          </div>
          <div className="mdl-card__actions mdl-card--border">
          <div className="mdl-layout-spacer"></div>
          </div>
        </div>
        <div className="mdl-cell--3-col mf-info-card mdl-card mdl-shadow--2dp">
          <div className="mdl-card__title mdl-card--expand">
            <h4>Complexes</h4>
            <h1>{this.state.json_req.complex_count}</h1>
          </div>
          <div className="mdl-card__actions mdl-card--border">
          <div className="mdl-layout-spacer"></div>
          </div>
        </div>
        <div className="mdl-cell--3-col mf-info-card mdl-card mdl-shadow--2dp">
          <div className="mdl-card__title mdl-card--expand">
            <h4>Branches</h4>
            <h1>{this.state.json_req.branch_count}</h1>
          </div>
          <div className="mdl-card__actions mdl-card--border">
          <div className="mdl-layout-spacer"></div>
          </div>
        </div>
      </div>
    </div>
  }
}


  ReactDOM.render(
    <OrderDashboard />,
    document.getElementById('content')
  );
