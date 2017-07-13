<?php
/**
 * 获取各个行政区的职位数量
 *
 * @param   资源句柄
 * @return  array
 */
function getDistrctNum($dbh)
{
    $sql = "select district, count(*) as num from `lagou` group by `district` order by num desc";
    $stat = $dbh->query($sql);
    $res = array();

    while ($row = $stat->fetch()) {
        $res[] = $row;
    }

    return $res;
}

/**
 * 获取指定行政区, 各个商业区的职位数量
 *
 * @param   资源句柄
 * @param   string
 * @return  array
 */
function getBizAreaNum($dbh, $district)
{
    $sql = "select biz_area, count(*) as num from lagou where district='$district' group by biz_area order by num desc";
    $stat = $dbh->query($sql);
    $res = array();

    while ($row = $stat->fetch()) {
        $res[] = $row;
    }

    return $res;
}

/**
 * 获取工作年限对应的职位数量
 *
 * @param   资源句柄
 * @return  array
 */
function getWorkYearNum($dbh)
{
    $sql = "select work_year, count(*) as num from lagou group by work_year order by num desc";
    $stat = $dbh->query($sql);
    $res = array();

    while ($row = $stat->fetch()) {
        $res[] = $row;
    }

    return $res;
}

/**
 * 根据工作年限获取薪资情况
 * 
 * @param   资源类型
 * @param   string
 * @return  array
 */
function getSalaryOfWorkYear($dbh, $year)
{
    $sql = "select salary from lagou where work_year ='$year'";
    $stat = $dbh->query($sql);
    $res = array();

    while ($row = $stat->fetch()) {
        $res[] = $row;
    }

    return $res;
}

/**
 * 获取行某政区工作年限的薪资情况
 *
 * @param   资源类型
 * @param   string
 * @param   string
 * @return  array
 */
function getSalaryByDist($dbh, $year, $district)
{
    $sql = "select salary from lagou where work_year ='$year' and district='$district'";
    $stat = $dbh->query($sql);
    $res = array();

    while ($row = $stat->fetch()) {
        $res[] = $row;
    }

    return $res;
}


try{
    $dbh = new PDO("sqlite:lagou.db");

    // 行政区职位信息分布情况
    $res = getDistrctNum($dbh);
    $districts = array();
    $districts_num = array();
    foreach ($res as $v) {
        array_push($districts, $v['district']);
        $districts_num[$v['district']] = $v['num'];
    }

    // 行政区前三个的商业区职位信息分布情况
    $first = $districts[0];
    $second = $districts[1];
    $third = $districts[2];

    $first_res = getBizAreaNum($dbh, $first);
    $res1 = array();
    $num1 = array();


    foreach ($first_res as $v) {
        array_push($res1, $v['biz_area']);
        array_push($num1, $v['num']);
    }

    $second_res = getBizAreaNum($dbh, $second);
    $res2 = array();
    $num2 = array();

    foreach ($second_res as $v) {
        array_push($res2, $v['biz_area']);
        array_push($num2, $v['num']);
    }

    $third_res = getBizAreaNum($dbh, $third);
    $res3 = array();
    $num3 = array();

    foreach ($third_res as $v) {
        array_push($res3, $v['biz_area']);
        array_push($num3, $v['num']);
    }

    // 工作年限对应的职位分布
    $year_num = getWorkYearNum($dbh);
    $res4 = array(
        '应届毕业生',
        '1年以下',
        '1-3年',
        '3-5年',
        '5-10年',
        '不限',
    );
    $num4 = array();

    foreach($res4 as $year) {
        foreach($year_num as $v) {
            if ($v['work_year'] == $year) {
                array_push($num4, $v['num']);
            }
        }
    }

    // (全深圳)工作年限对应的平均薪资情况
    $salary = array();
    foreach ($res4 as $year) {
        $salary_res = getSalaryOfWorkYear($dbh, $year);
        $tmp_arr = array();

        foreach ($salary_res as $v) {
            array_push($tmp_arr, intval($v['salary']));
        }
        sort($tmp_arr);
        array_pop($tmp_arr);
        array_shift($tmp_arr);

        $sum = 0;
        foreach($tmp_arr as $v) {
            $sum += $v;
        }
        $rank = intval($sum / count($tmp_arr) * 1000);

        array_push($salary, $rank);
    }

    // (前三行政区区)工作年限对应的平均薪资情况
    $salary1 = array();
    foreach ($res4 as $year) {
        $salary_res = getSalaryByDist($dbh, $year, $first);
        $tmp_arr = array();

        foreach ($salary_res as $v) {
            array_push($tmp_arr, intval($v['salary']));
        }
        sort($tmp_arr);
        array_pop($tmp_arr);
        array_shift($tmp_arr);

        $sum = 0;
        foreach($tmp_arr as $v) {
            $sum += $v;
        }
        $rank = intval($sum / count($tmp_arr) * 1000);

        array_push($salary1, $rank);
    }
    $salary2 = array();
    foreach ($res4 as $year) {
        $salary_res = getSalaryByDist($dbh, $year, $second);
        $tmp_arr = array();

        foreach ($salary_res as $v) {
            array_push($tmp_arr, intval($v['salary']));
        }
        sort($tmp_arr);
        array_pop($tmp_arr);
        array_shift($tmp_arr);

        $sum = 0;
        foreach($tmp_arr as $v) {
            $sum += $v;
        }
        $rank = intval($sum / count($tmp_arr) * 1000);

        array_push($salary2, $rank);
    }
    $salary3 = array();
    foreach ($res4 as $year) {
        $salary_res = getSalaryByDist($dbh, $year, $third);
        $tmp_arr = array();

        foreach ($salary_res as $v) {
            array_push($tmp_arr, intval($v['salary']));
        }
        sort($tmp_arr);
        array_pop($tmp_arr);
        array_shift($tmp_arr);

        $sum = 0;
        foreach($tmp_arr as $v) {
            $sum += $v;
        }
        $rank = intval($sum / count($tmp_arr) * 1000);

        array_push($salary3, $rank);
    }

} catch (PDOException $e) {
    echo "连接失败: " . $e->getMessage();
} finally {
    require_once('analysis.html');
}
