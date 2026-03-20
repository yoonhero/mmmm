# Hello, World! Combinatorial Game Theory

# 이 공부는 생각하면 할수록 불리한 구조의 게임을 만들기 위한 일환으로 시작되었습니다.
# idea: 무한재귀성(e.g. 가위바위보 예측)
# -> 생각해보면 combinatorial game theory와 완전히 반대 상황이라면(?)
#    - randomness
#    - no fixed-point
# Combinatorial Game Theory는 사실요 DAG입니다.
# Two-Player / Perfect Information / No Randomness / Deterministic Outcome
#
# partially: available moves depend on which players move it is (chess)
# normal game: NIM!
#
# Game States - N-state(current win)/P-state(position)
#
# NIM -> a^b^c...^z=0(필패) otherwise (필승)
# (pf by me)
#   1) K=2일 때
#       a=1, b=1일 때 -> 필패
#       a=m, b=m일 때 -> 내가 몇개를 가져가도 그만큼 상대가 가져가면 강귀납에 따라서 필패
#       XOR은 표수가 2인 체에서 정의된 벡터공간과 동치이다. 따라서 assoc이 성립하게 되며 이렇게 해석할 수 있다.
#       10^(11)=10^(10^1)=(10^10)^1=1 -> m>n일 때 m-n개가 남은 것과 같은 상태임을 쉽게 알 수 있으므로
#       m=n일 때만 필패
#   2) K=N일 때
#       a^b를 해서 하나의 pile로 만들고 귀납가설에 따라서 성립
#
# Sprague Grundy theorem(impartial / normal / finite game)
# - Intuition: single pile Nim(=grundy num)으로 환원시키자!
# - Summary: 현재 상태에서 가능한 상태들로 갔을 때의 set의 MEX 값이 grundy num이 됨.
# (pf)
#   g(G) = mex{g(H) | G->H} / mex(S) = min(S \subsets N) -> DAG 직관으로
#   [claim]: g(G+H) = g(G) ^ g(H) -> 가 성립하므로 NIM처럼 해석 가능!
#   [lemma]: G+*g(G) is P-position + G+*m is N-position(s.t. m<g(G))
#   (pf I)
#       1) G->H: g(H) \neq n -> definition of mex
#           new state: H+*n 
#           a) g(H)=m<n: *n->*m 귀납가설에 의해서 P
#           b) g(H)=m>n: N-position by(II)
#       2) *n->*m with m<n: mex 정의에 따라서 g(H)=m인 H로 이동가능. P
#   (pf II) goto H s.t. g(H)=*m -> N
#   G~*g(G) -> equivalent class!
#   [main pf] g(G+H)=mex{g(G'+H) s.t. G->G' U g(G+H') s.t. H->H'}=g(G)^g(H)
#       1) a^b \in S -> 모순 g(G')=a or g(H')=b가 됨.
#       2) \all t < a^b in S -> mex와 xor의 성질로 자명.
#
# e.g. 31game grundy number: 0 1 2 3 0 1 2 3 0 1 2 3 ...
# e.g. BOJ13034: 선분 선택 시 partition이 되고 독립적인 게임이 됨. 여기에 SG thm.