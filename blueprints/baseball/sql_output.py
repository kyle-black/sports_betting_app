import sqlite3
import pandas as pd


conn = sqlite3.connect('mlb_games.db')

sql_query = '''
SELECT
    upcoming_games.game_id,
    upcoming_games.away_team AS away_tm,
	upcoming_games.home_team AS home_tm,
    upcoming_games.time AS game_date,
    
    home_team_batting."Tm" AS home_tm,
    home_team_batting."#Bat" AS home_bat,
    home_team_batting."BatAge" AS home_bat_age,
	home_team_batting."R/G" AS home_bat_R_G,
	home_team_batting."G" AS home_bat_G,
	home_team_batting."PA" AS home_bat_PA,
	home_team_batting."AB" AS home_bat_AB,
	home_team_batting."R" AS home_bat_R,
	home_team_batting."H" AS home_bat_H,
	home_team_batting."2B" AS home_bat_2B,
	home_team_batting."3B" AS home_bat_3B,
	home_team_batting."HR" AS home_bat_HR,
	home_team_batting."RBI" AS home_bat_RBI,
	home_team_batting."SB" AS home_bat_SB,
	home_team_batting."CS" AS home_bat_CS,
	home_team_batting."BB" AS home_bat_BB,
	home_team_batting."SO" AS home_bat_SO,
	home_team_batting."BA" AS home_bat_BA,
	home_team_batting."OBP" AS home_bat_OBP,
	home_team_batting."SLG" AS home_bat_SLG,
	home_team_batting."OPS" AS home_bat_OPS,
	home_team_batting."OPS+" AS home_bat_OPS_plus,
	home_team_batting."TB" AS home_bat_TB,
	home_team_batting."GDP" AS home_bat_GDP,
	home_team_batting."HBP" AS home_bat_HBP,
	home_team_batting."SH" AS home_bat_SH,
	home_team_batting."SF" AS home_bat_SF,
	home_team_batting."IBB" AS home_bat_IBB,
	home_team_batting."LOB" AS home_bat_LOB,
	
	away_team_batting."Tm" AS away_tm,
	away_team_batting."#Bat" AS away_bat,
    away_team_batting."BatAge" AS away_bat_age,
	away_team_batting."R/G" AS away_bat_R_G,
	away_team_batting."G" AS away_bat_G,
	away_team_batting."PA" AS away_bat_PA,
	away_team_batting."AB" AS away_bat_AB,
	away_team_batting."R" AS away_bat_R,
	away_team_batting."H" AS away_bat_H,
	away_team_batting."2B" AS away_bat_2B,
	away_team_batting."3B" AS away_bat_3B,
	away_team_batting."HR" AS away_bat_HR,
	away_team_batting."RBI" AS away_bat_RBI,
	away_team_batting."SB" AS away_bat_SB,
	away_team_batting."CS" AS away_bat_CS,
	away_team_batting."BB" AS away_bat_BB,
	away_team_batting."SO" AS away_bat_SO,
	away_team_batting."BA" AS away_bat_BA,
	away_team_batting."OBP" AS away_bat_OBP,
	away_team_batting."SLG" AS away_bat_SLG,
	away_team_batting."OPS" AS away_bat_OPS,
	away_team_batting."OPS+" AS away_bat_OPS_plus,
	away_team_batting."TB" AS away_bat_TB,
	away_team_batting."GDP" AS away_bat_GDP,
	away_team_batting."HBP" AS away_bat_HBP,
	away_team_batting."SH" AS away_bat_SH,
	away_team_batting."SF" AS away_bat_SF,
	away_team_batting."IBB" AS away_bat_IBB,
	away_team_batting."LOB" AS away_bat_LOB,
	
	home_team_fielding."Tm" AS home_tm,
	home_team_fielding."RA/G" as home_fld_RA_G,
	home_team_fielding."DefEff" as home_fld_DefEff,
	home_team_fielding."G" as home_fld_G,
	home_team_fielding."GS" as home_fld_GS,
	home_team_fielding."CG" as home_fld_CG,
	home_team_fielding."Inn" as home_fld_INN,
	home_team_fielding."Ch" as home_fld_CH,
	home_team_fielding."PO" as home_fld_PO,
	home_team_fielding."A" as home_fld_A,
	home_team_fielding."E" as home_fld_E,
	home_team_fielding."DP" as home_fld_DP,
	home_team_fielding."Fld%" as home_fld_FLD_PCT,
	home_team_fielding."Rtot" as home_fld_CH,
	home_team_fielding."Rtot/yr" as home_fld_Rtot_yr,
	home_team_fielding."Rdrs" as home_fld_Rdrs,
	home_team_fielding."Rdrs/yr" as home_fld_Rdrs_yrs,
	home_team_fielding."Rgood" as home_fld_Rgood,
	
	away_team_fielding."Tm" AS away_tm,
	away_team_fielding."RA/G" as away_fld_RA_G,
	away_team_fielding."DefEff" as away_fld_DefEff,
	away_team_fielding."G" as away_fld_G,
	away_team_fielding."GS" as away_fld_GS,
	away_team_fielding."CG" as away_fld_CG,
	away_team_fielding."Inn" as away_fld_INN,
	away_team_fielding."Ch" as away_fld_CH,
	away_team_fielding."PO" as away_fld_PO,
	away_team_fielding."A" as away_fld_A,
	away_team_fielding."E" as away_fld_E,
	away_team_fielding."DP" as away_fld_DP,
	away_team_fielding."Fld%" as away_fld_FLD_PCT,
	away_team_fielding."Rtot" as away_fld_CH,
	away_team_fielding."Rtot/yr" as away_fld_Rtot_yr,
	away_team_fielding."Rdrs" as away_fld_Rdrs,
	away_team_fielding."Rdrs/yr" as away_fld_Rdrs_yrs,
	away_team_fielding."Rgood" as away_fld_Rgood,
	
	home_team_pitching."Tm" AS home_tm,
	
	home_team_pitching."RA/G" AS home_pitch_RA_G,
	home_team_pitching."W" AS home_pitch_W,
	home_team_pitching."L" AS home_pitch_L,
	home_team_pitching."W-L%" AS home_pitch_W_L_pct,
	home_team_pitching."ERA" AS home_pitch_ERA,
	home_team_pitching."G" AS home_pitch_G,
	home_team_pitching."GS" AS home_pitch_GS,
	home_team_pitching."GF" AS home_pitch_GF,
	home_team_pitching."CG" AS home_pitch_CG,
	home_team_pitching."tSho" AS home_pitch_tSho,
	home_team_pitching."cSho" AS home_pitch_cSho,
	home_team_pitching."SV" AS home_pitch_SV,
	home_team_pitching."IP" AS home_pitch_IP,
	home_team_pitching."H" AS home_pitch_H,
	home_team_pitching."R" AS home_pitch_R,
	home_team_pitching."ER" AS home_pitch_ER,
	home_team_pitching."HR" AS home_pitch_HR,
	home_team_pitching."BB" AS home_pitch_BB,
	home_team_pitching."IBB" AS home_pitch_IBB,
	home_team_pitching."SO" AS home_pitch_SO,
	home_team_pitching."HBP" AS home_pitch_HBP,
	home_team_pitching."BK" AS home_pitch_BK,
	home_team_pitching."WP" AS home_pitch_WP,
	home_team_pitching."BF" AS home_pitch_BF,
	home_team_pitching."ERA+" AS home_pitch_ERA_plus,
	home_team_pitching."FIP" AS home_pitch_FIP,
	home_team_pitching."WHIP" AS home_pitch_WHIP,
	home_team_pitching."H9" AS home_pitch_H9,
	home_team_pitching."HR9" AS home_pitch_HR9,
	home_team_pitching."BB9" AS home_pitch_BB9,
	home_team_pitching."SO9" AS home_pitch_SO9,
	home_team_pitching."SO/W" AS home_pitch_SO_W,
	home_team_pitching."LOB" AS home_pitch_LOB,
	
	
	away_team_pitching."Tm" AS away_tm,
	
	away_team_pitching."RA/G" AS away_pitch_RA_G,
	away_team_pitching."W" AS away_pitch_W,
	away_team_pitching."L" AS away_pitch_L,
	away_team_pitching."W-L%" AS away_pitch_W_L_pct,
	away_team_pitching."ERA" AS away_pitch_ERA,
	away_team_pitching."G" AS away_pitch_G,
	away_team_pitching."GS" AS away_pitch_GS,
	away_team_pitching."GF" AS away_pitch_GF,
	away_team_pitching."CG" AS away_pitch_CG,
	away_team_pitching."tSho" AS away_pitch_tSho,
	away_team_pitching."cSho" AS away_pitch_cSho,
	away_team_pitching."SV" AS away_pitch_SV,
	away_team_pitching."IP" AS away_pitch_IP,
	away_team_pitching."H" AS away_pitch_H,
	away_team_pitching."R" AS away_pitch_R,
	away_team_pitching."ER" AS away_pitch_ER,
	away_team_pitching."HR" AS away_pitch_HR,
	away_team_pitching."BB" AS away_pitch_BB,
	away_team_pitching."IBB" AS away_pitch_IBB,
	away_team_pitching."SO" AS away_pitch_SO,
	away_team_pitching."HBP" AS away_pitch_HBP,
	away_team_pitching."BK" AS away_pitch_BK,
	away_team_pitching."WP" AS away_pitch_WP,
	away_team_pitching."BF" AS away_pitch_BF,
	away_team_pitching."ERA+" AS away_pitch_ERA_plus,
	away_team_pitching."FIP" AS away_pitch_FIP,
	away_team_pitching."WHIP" AS away_pitch_WHIP,
	away_team_pitching."H9" AS away_pitch_H9,
	away_team_pitching."HR9" AS away_pitch_HR9,
	away_team_pitching."BB9" AS away_pitch_BB9,
	away_team_pitching."SO9" AS away_pitch_SO9,
	away_team_pitching."SO/W" AS away_pitch_SO_W,
	away_team_pitching."LOB" AS away_pitch_LOB
FROM upcoming_games
LEFT JOIN weighted_team_batting AS home_team_batting ON upcoming_games.home_team = home_team_batting.Tm 
LEFT JOIN weighted_team_batting AS away_team_batting ON upcoming_games.away_team = away_team_batting.Tm
LEFT JOIN weighted_team_fielding AS home_team_fielding ON upcoming_games.home_team = home_team_fielding.Tm
LEFT JOIN weighted_team_fielding AS away_team_fielding ON upcoming_games.away_team = away_team_fielding.Tm 
LEFT JOIN weighted_team_pitching AS home_team_pitching ON upcoming_games.home_team = home_team_pitching.Tm
LEFT JOIN weighted_team_pitching AS away_team_pitching ON upcoming_games.away_team = away_team_pitching.Tm


;


'''





data_pull = pd.read_sql_query(sql_query,conn)



print(data_pull)
conn.close()

