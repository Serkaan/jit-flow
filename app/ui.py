import os, requests, pandas as pd, streamlit as st
API=os.getenv('API_URL','http://127.0.0.1:8080')
st.set_page_config(page_title='JIT-Flow',page_icon='🔐',layout='wide')
st.title('🔐 JIT-Flow');st.caption('Just-In-Time Yetki Yönetimi')
if 'token' not in st.session_state: st.session_state.token=None
if not st.session_state.token:
    with st.form('login'):
        user=st.text_input('Kullanıcı adı',value='requester');pwd=st.text_input('Parola',type='password',value='demo');go=st.form_submit_button('Giriş')
    if go:
        r=requests.post(API+'/api/auth/token',data={'username':user,'password':pwd},timeout=10)
        if r.ok:st.session_state.token=r.json()['access_token'];st.rerun()
        else:st.error(r.text)
    st.stop()
H={'Authorization':'Bearer '+st.session_state.token}
me=requests.get(API+'/api/me',headers=H,timeout=10).json();st.sidebar.success(f"{me['display_name']} · {me['role']}")
if st.sidebar.button('Çıkış'):st.session_state.token=None;st.rerun()
page=st.sidebar.radio('Menü',['Yeni Talep','Taleplerim','Onay Merkezi','Audit Kayıtları'])
if page=='Yeni Talep':
    st.subheader('Yeni Yetki Talebi')
    with st.form('request'):
        user=st.selectbox('Hedef kullanıcı',['ahmet','mehmet','ayse','fatma']);group=st.selectbox('AD grubu',['Helpdesk Readers','SQL Operators','File Share Admins','Backup Operators','Server Operators','DnsAdmins','Domain Admins']);duration=st.number_input('Süre (dakika)',5,480,60);just=st.text_area('Gerekçe');send=st.form_submit_button('Talebi oluştur',type='primary')
    if send:
        r=requests.post(API+'/api/request',headers=H,json={'text':f'{user} için {duration} dakika {group} yetkisi. Gerekçe: {just}','target_samaccountname':user,'target_group':group,'duration_minutes':duration,'justification':just},timeout=20)
        if r.ok:
            d=r.json();st.success(f"Talep #{d['request']['id']} oluşturuldu");st.metric('Risk',f"{d['request']['risk_score']}/100",d['request']['risk_level']);st.info(d['request']['risk_summary'])
        else:st.error(r.text)
elif page=='Taleplerim':
    d=requests.get(API+'/api/requests',headers=H,timeout=10).json();st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
elif page=='Onay Merkezi':
    if me['role'] not in ['Admin','Manager']:st.warning('Bu ekran yalnızca yönetici rollerine açıktır');st.stop()
    rows=requests.get(API+'/api/requests?status=Pending',headers=H,timeout=10).json()
    if not rows:st.info('Bekleyen talep yok')
    for r in rows:
        with st.container(border=True):
            st.subheader(f"Talep #{r['id']} · {r['target_user']} → {r['target_group']}");c1,c2,c3=st.columns(3);c1.metric('Risk',f"{r['risk_score']}/100",r['risk_level']);c2.metric('Süre',f"{r['duration_minutes']} dk");c3.write(r['justification']);ack=st.checkbox('Yüksek riski kabul ediyorum',key=f"a{r['id']}");a,b=st.columns(2)
            if a.button('Onayla',key=f"ok{r['id']}",type='primary'):
                x=requests.post(API+f"/api/approve/{r['id']}",headers=H,json={'acknowledge_risk':ack},timeout=10);st.success('Onaylandı') if x.ok else st.error(x.text);st.rerun()
            if b.button('Reddet',key=f"no{r['id']}"):
                x=requests.post(API+f"/api/reject/{r['id']}",headers=H,json={'reason':'Yönetici tarafından reddedildi'},timeout=10);st.rerun()
else:
    if me['role'] not in ['Admin','Manager']:st.warning('Yetkisiz');st.stop()
    d=requests.get(API+'/api/audit',headers=H,timeout=10).json();st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
