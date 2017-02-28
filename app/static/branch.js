/*** @jsx React.DOM */
class BranchRow extends React.Component {
	constructor(props) {
		super(props)
	}

	render() {
		return <tr>
			<td className="mdl-data-table__cell--non-numeric">{this.props.branch.branch_id}</td>
			<td className="mdl-data-table__cell--non-numeric">{this.props.branch.name}</td>
			<td className="mdl-data-table__cell--non-numeric">
				<address>
					<div>{this.props.branch.address1}</div>
					<div>{this.props.branch.address2 && this.props.branch.address2 != 'NULL' ? this.props.branch.address2 : ''}</div>
				</address>
			</td>
			<td className="mdl-data-table__cell--non-numeric">{this.props.branch.city}</td>
			<td className="mdl-data-table__cell--non-numeric">{this.props.branch.state}</td>
			<td className="mdl-data-table__cell--non-numeric">{this.props.branch.zip}</td>
		</tr>
	}
}

class BranchPage extends React.Component {
	constructor(props) {
		super(props)
		this.state={pageItems:null, db_class:'Branch', db_col:'pk_id', asc: true}
		this.handleClick = this.handleClick.bind(this);
		this.buildUrl = this.buildUrl.bind(this);
		this.callQuery = this.callQuery.bind(this);
	}

	componentDidMount() {
		this.callQuery();
	}

	handleClick(db_class, db_col) {
		event.preventDefault();
		let new_direction = !this.state.asc;
		this.setState({db_class:db_class, db_col:db_col, asc: new_direction});
	}

	callQuery() {
		let path = window.location.pathname == '/' ? '' : window.location.pathname;
		let query_string = window.location.search.slice(1);
		let request_url = this.props.api_path+path+'?'+query_string;
		let request = new XMLHttpRequest();
		request.onreadystatechange = (e) => {
			if (request.readyState !== 4) {
				return;
			}

			if (request.status === 200) {
				let json_req = JSON.parse(request.response)
				this.setState({pageItems:json_req});
			} else {
				console.warn('error');
			}
		};
		request.open('GET', request_url);
		request.send();
	}

	buildUrl() {
		let request_url = (this.state.pageItems && this.state.pageItems.page) > 1 ? this.props.api_path+'/branch/'+page_num : this.props.api_path;
		let query_string = '?sort='+this.state.db_class+'&col='+this.state.db_col+'&direction='+this.getAllUrlParams().direction
		return request_url+query_string;
	}

	buildLink(path) {
		let pathname = path == '1' ? '' : path;
		let params = window.location.search.slice(1).length > 0 ? '?'+window.location.search.slice(1) : window.location.search.slice(1);
		let request_url = path+params;
		return '/branch/'+request_url;
	}

	getAllUrlParams(url) {

		// get query string from url (optional) or window
		var queryString = url ? url.split('?')[1] : window.location.search.slice(1);

		// we'll store the parameters here
		var obj = {};

		// if query string exists
		if (queryString) {

			// stuff after # is not part of query string, so get rid of it
			queryString = queryString.split('#')[0];

			// split our query string into its component parts
			var arr = queryString.split('&');

			for (var i=0; i<arr.length; i++) {
				// separate the keys and the values
				var a = arr[i].split('=');

				// in case params look like: list[]=thing1&list[]=thing2
				var paramNum = undefined;
				var paramName = a[0].replace(/\[\d*\]/, function(v) {
					paramNum = v.slice(1,-1);
					return '';
				});

				// set parameter value (use 'true' if empty)
				var paramValue = typeof(a[1])==='undefined' ? true : a[1];

				// (optional) keep case consistent
				paramName = paramName.toLowerCase();
				paramValue = paramValue.toLowerCase();

				// if parameter name already exists
				if (obj[paramName]) {
					// convert value to array (if still string)
					if (typeof obj[paramName] === 'string') {
						obj[paramName] = [obj[paramName]];
					}
					// if no array index number specified...
					if (typeof paramNum === 'undefined') {
						// put the value on the end of the array
						obj[paramName].push(paramValue);
					}
					// if array index number specified...
					else {
						// put the value at that index number
						obj[paramName][paramNum] = paramValue;
					}
				}
				// if param name doesn't exist yet, set it
				else {
					obj[paramName] = paramValue;
				}
			}
		}

		return obj;
	}

	buildLinkSort() {
		let _dir = this.getAllUrlParams().direction;
		let dir = !(_dir == 'asc') ? 'asc' : 'desc';
		return '/'+this.state.pageItems.paginate.page+'?sort='+this.state.db_class+'&col='+this.state.db_col+'&direction='+dir
	}

	render() {
		return <div className="demo-charts mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col mdl-grid">
			{ this.state.pageItems ?
				<div>
				{
					this.state.pageItems.paginate.pages > 1 ?
						<div className="mdl-paging">
							<span className="mdl-paging__per-page"><span className="mdl-paging__per-page-label">Results per page:</span><span className="mdl-paging__per-page-value">{this.state.pageItems.paginate.per_page}</span></span>
							{this.state.pageItems.paginate.has_prev ? <a id="prev-page" href={this.buildLink(this.state.pageItems.paginate.prev_num)} className="mdl-button mdl-js-button mdl-js-ripple-effect mdl-button--icon mdl-paging__prev"><i className="material-icons">keyboard_arrow_left</i></a> : ''}
						 <span className="mdl-paging__count">{this.state.pageItems.paginate.page} de {this.state.pageItems.paginate.pages}</span>
							 {this.state.pageItems.paginate.has_next ? <a id="next-page" href={this.buildLink(this.state.pageItems.paginate.next_num)} className="mdl-button mdl-js-button mdl-js-ripple-effect mdl-button--icon mdl-paging__next"><i className="material-icons">keyboard_arrow_right</i></a> : ''}
						</div>
						:
						''
				}
				<table className="mdl-data-table mdl-js-data-table">
					<thead>
						<tr>
							<th className="mdl-data-table__cell--non-numeric">Branch Number</th>
							<th className="mdl-data-table__cell--non-numeric">Name</th>
							<th className="mdl-data-table__cell--non-numeric">Address</th>
							<th className="mdl-data-table__cell--non-numeric">City</th>
							<th className="mdl-data-table__cell--non-numeric">State</th>
							<th className="mdl-data-table__cell--non-numeric">Zip</th>
						</tr>
					</thead>
					<tbody>
						{this.state.pageItems.branches.map((branch, i) => {
							return <BranchRow key={i} branch={branch} />
						})}
					</tbody>
				</table>
			</div>
				:<div className="mdl-spinner mdl-js-spinner is-active"></div>
			}
		</div>
		;
	}
}

BranchPage.defaultProps = {api_path:'/api'};

ReactDOM.render(
	<BranchPage />,
	document.getElementById('content')
);
