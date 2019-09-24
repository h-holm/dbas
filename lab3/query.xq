(: let $d:=doc("mondial.xml") :)

(: test :)
(: return $d/mondial/country/name :)

(: Lab 3 Question a) :)
(: for $m in $d/mondial/mountain :)
(: where ($m[@type = "volcano"]) :)
(: return $m/name/text() NOT THIS ONE :)
(: return $m/name :)

(: Lab 3 Question b) :)
(: for $m in $d/mondial/mountain :)
(: where ($m/mountains/text() = "Hawaii") and ($m[@type = "volcano"]) :)
(: return $m/name/text() NOT THIS ONE :)
(: return $m/name :)

(: Lab 3 Question c) Notice that the xs:float conversion is redundant :)
(: for $m in $d/mondial/mountain :)
(: where (xs:float($m/elevation) > xs:float(8000)) :)
(: return $m/name/text() NOT THIS ONE :)
(: return <bigmountain><height>{data($m/elevation)} meters</height><name>{$m/name/text()}</name></bigmountain> :)
