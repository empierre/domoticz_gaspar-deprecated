#!/usr/bin/perl
use DBI;
my ($from,$to)=@ARGV;

my $dbh = DBI->connect('dbi:SQLite:dbname=domoticz.db','','',{AutoCommit=>1,RaiseError=>1,PrintError=>0});

my $fst = $dbh->selectall_arrayref("select * from Meter_Calendar where DeviceRowID=$from;");
foreach my $row (@$fst) {
  my ($n,$a,$c,$b)=@$row;
  print "DELETE FROM 'Meter_Calendar' WHERE devicerowid=$to and date = \"$c\";insert into Meter_Calendar (DeviceRowID,Value,Date,Counter) VALUES ($to,$a,\"$c\",$b)\n";
}

my $fst = $dbh->selectall_arrayref("select * from Meter where DeviceRowID=$from;");
foreach my $row (@$fst) {
  my ($n,$a,$c,$b)=@$row;
  #print "a: $a ".($b/10)." $c\n";
  print "insert into Meter (DeviceRowID,Value,Date,Usage) VALUES ($to,".($b/10).",\"$c\",$a)\n";
}

$dbh->disconnect;
