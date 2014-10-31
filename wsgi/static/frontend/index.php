<?php
$row = 1;
/*
if (($handle = fopen("test.csv", "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
        $num = count($data);
	
        for ($c=19; $c < $num; $c++) {
	    if($data[$c] == ""){
			$c+=4;
	    }
	    else{
			echo $data[$c] . "<br />\n";
			$parsed[$c-19] = $data[$c];
	    }
        }
    }
    fclose($handle);
}
*/

/*
$file = file_get_contents("test.csv");
$parsing = explode("\n\r", $file);
echo $parsing[0];
*/
?>


<html>
	<head>
		<link rel="stylesheet" type="text/css" href="style.css">
		<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
		<script src="js/bootstrap.min.js"></script>
		<script src="jsonify.js"></script>
		<link href="css/bootstrap.min.css" rel="stylesheet">
		<link href="css/datepicker.css" rel="stylesheet">
		<link rel="stylesheet" href="css/font-awesome.min.css">
	</head>
	<body>
		<!-- input form in table format, loop entries -->
		<div class="indent">
			<h2>Purchases</h2>
			<div class="indent">
				<table id="purchases" class="form-group">
					<tr>
						<th>Day</th>
						<th>Month</th>
						<th>Year</th>
						<th># Shares</th>
						<th>Expense</th>
					</tr>
					<?php 
						for($i = 0; $i < 10; $i++){
							echo 	'	<tr>
											<td class="col-md-1">
												<input type="text" id="pday'. $i .'" class="form-control">
											</td>
											<td class="col-md-1">
												<input type="text" id="pmonth'. $i .'" class="form-control">
											</td>
											<td class="col-md-1">
												<input type="text" id="pyear'. $i .'" class="form-control">
											</td>
											<td class="col-md-2">
												<input type="text" id="pshare'. $i .'" class="form-control">
											</td>
											<td class="col-md-6">
												<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="pvalue'. $i .'" class="value form-control"></div>
											</td>
										</tr>
									';
						}
					?>
				</table>
			</div>

			<h2>Sales</h2>
			<div class="indent">
				<table id="sales" class="form-group">
					<tr>
						<th>Day</th>
						<th>Month</th>
						<th>Year</th>
						<th># Shares</th>
						<th>Revenue</th>
					</tr>
					<?php 
						for($i = 0; $i < 10; $i++){
							echo 	'	<tr>
											<td class="col-md-1">
												<input type="text" id="sday'. $i .'" class="form-control">
											</td>
											<td class="col-md-1">
												<input type="text" id="smonth'. $i .'" class="form-control">
											</td>
											<td class="col-md-1">
												<input type="text" id="syear'. $i .'" class="form-control">
											</td>
											<td class="col-md-2">
												<input type="text" id="sshare'. $i .'" class="form-control">
											</td>
											<td class="col-md-6">
												<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="svalue'. $i .'" class="value form-control"></div>
											</td>
										</tr>
									';
						}
					?>
				</table>
				</table>
			</div>
			<a href="#" class="btn btn-default" onclick="inputToJSON()">Compute</a>
		</div>
		<div>
			<textarea cols="10" rows="10" id="request-data"></textarea>
		</div>
	</body>
</html>