var SelectPicker = React.createClass({
  componentDidMount: function () {
  	$(this.refs.selectPicker).selectpicker({
    	liveSearch: true
    });
  },

  getInitialState: function () {
    return {
      value: optionItems[0]
    }
  },

  _onChange: function(){
  	console.log('change');
  },

  render: function() {
  	var options = this.props.items.map((object, i) =>
  		<option key={i} value={object}>
  			{object}
  		</option>
  	);

    return <div className="selectWrapper">
    	<label htmlFor={"selectNum"}>Number</label>
      <select id={"selectNum"}
      	ref="selectPicker"
      	className="form-control"
      	onChange={this._onChange}
      	value={this.state.value}>
      		{options}
      </select>
  	</div>;
  }
});

var optionItems = ['1', '2', '3', '4', '5', '6'];

ReactDOM.render(
  <SelectPicker items={optionItems} />,
  document.getElementById('container')
);
