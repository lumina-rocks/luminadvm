<script setup>


import {EventBuilder, Filter, Tag, Timestamp} from "@rust-nostr/nostr-sdk";
import store from '../store';
import miniToastr from "mini-toastr";
import VueNotifications from "vue-notifications";
import {ref} from "vue";
import {sleep} from "../components/helper/Helper.vue"
import {zap} from "@/components/helper/Zap.vue";

let dvms = []
let requestids = []

async function summarizefeed(eventids) {

  listen()


  let sortedIds = eventids.sort(function (a, b) {
    return (a.index > b.index) ? 1 : ((b.index > a.index) ? -1 : 0);
  });

  try {
    if (store.state.pubkey === undefined || localStorage.getItem('nostr-key-method') === "anon") {
      miniToastr.showMessage("In order to receive personalized recommendations, sign-in first.", "Not signed in.", VueNotifications.types.warn)
      return
    }

    dvms = []
    store.commit('set_summarization_dvms', dvms)

    let client = store.state.client
    let content = "NIP 90 Summarization request"
    let kind = 5001

    let tags = []
    for (const tag of sortedIds) {
      try {
        tags.push(["i", tag.id, "event"])
      } catch {
      }
    }

    let r = ["relays"]
    for (let relay of store.state.relays) {
      r.push(relay)
    }
    tags.push(r)


    let res;
    let requestid;


    let tags_t = []
    for (let tag of tags) {
      tags_t.push(Tag.parse(tag))
    }
    let evt = new EventBuilder(kind, content, tags_t)
    res = await client.sendEventBuilder(evt);
    requestid = res.toHex();
    console.log(res)


    requestids.push(requestid)
    store.commit('set_current_request_id_summarization', requestids)


  } catch (error) {
    console.log(error);
  }
}


async function listen() {
  let client = store.state.client
  let pubkey = store.state.pubkey

  const filter = new Filter().kinds([7000, 6001]).pubkey(pubkey).since(Timestamp.now());
  await client.subscribe([filter]);

  const handle = {
    // Handle event
    handleEvent: async (relayUrl, subscriptionId, event) => {
      /*   if (store.state.summarizationhasEventListener === false){
           return true
         }*/
      //const dvmname =  getNamefromId(event.author.toHex())
      console.log("Received new event from", relayUrl);
      console.log(event.asJson())
      let resonsetorequest = false
      sleep(0).then(async () => {
        for (let tag in event.tags) {
          if (event.tags[tag].asVec()[0] === "e") {

            if (store.state.requestidSummarization.includes(event.tags[tag].asVec()[1])) {
              resonsetorequest = true
            }
          }

        }
        if (resonsetorequest === true) {
          if (event.kind === 7000) {


            try {
              console.log("7000: ", event.content);
              console.log("DVM: " + event.author.toHex())

              let status = "unknown"
              let jsonentry = {
                id: event.author.toHex(),
                kind: "",
                status: status,
                result: [],
                name: event.author.toBech32(),
                about: "",
                image: "",
                amount: 0,
                bolt11: ""
              }

              for (const tag in event.tags) {
                if (event.tags[tag].asVec()[0] === "status") {
                  status = event.tags[tag].asVec()[1]
                }

                if (event.tags[tag].asVec()[0] === "amount") {
                  jsonentry.amount = event.tags[tag].asVec()[1]
                  if (event.tags[tag].asVec().length > 2) {
                    jsonentry.bolt11 = event.tags[tag].asVec()[2]
                  } else {
                    let profiles = await get_user_infos([event.author.toHex()])
                    let created = 0
                    let current
                    console.log("NUM KIND0 FOUND " + profiles.length)
                    if (profiles.length > 0) {
                      // for (const profile of profiles){
                      console.log(profiles[0].profile)
                      let current = profiles[0]
                      // if (profiles[0].profile.createdAt > created){
                      //     created = profile.profile.createdAt
                      //     current = profile
                      //   }


                      let lud16 = current.profile.lud16
                      if (lud16 !== null && lud16 !== "") {
                        console.log("LUD16: " + lud16)
                        jsonentry.bolt11 = await createBolt11Lud16(lud16, jsonentry.amount)
                        console.log(jsonentry.bolt11)
                        if (jsonentry.bolt11 === "") {
                          status = "error"
                        }
                      } else {
                        console.log("NO LNURL")
                      }

                    } else {
                      console.log("PROFILE NOT FOUND")
                    }
                  }
                }
              }


              //let dvm = store.state.nip89dvms.find(x => JSON.parse(x.event).pubkey === event.author.toHex())
              for (const el of store.state.nip89dvms) {
                if (JSON.parse(el.event).pubkey === event.author.toHex().toString()) {
                  jsonentry.name = el.name
                  jsonentry.about = el.about
                  jsonentry.picture = el.picture

                  console.log(jsonentry)

                }
              }
              if (dvms.filter(i => i.id === jsonentry.id).length === 0) {

                dvms.push(jsonentry)
              }
              /*if (event.content !== ""){
                status = event.content
              }*/

              dvms.find(i => i.id === jsonentry.id).status = status
              store.commit('set_summarization_dvms', dvms)

            } catch (error) {
              console.log("Error: ", error);
            }


          } else if (event.kind === 6001) {
            console.log(event.content)
            dvms.find(i => i.id === event.author.toHex()).result = event.content
            dvms.find(i => i.id === event.author.toHex()).status = "finished"
            store.commit('set_summarization_dvms', dvms)
          }
        }
      })
    },
    // Handle relay message
    handleMsg: async (relayUrl, message) => {
      //console.log("Received message from", relayUrl, message.asJson());
    }
  };

  client.handleNotifications(handle);
}


async function zap_local(invoice) {

  let success = await zap(invoice)
  if (success) {
    dvms.find(i => i.bolt11 === invoice).status = "paid"
    store.commit('set_summarization_dvms', dvms)
  }

}

defineProps({
  events: {
    type: Array,
    required: false
  },
})


const isModalOpened = ref(false);
const modalcontent = ref("");
const datetopost = ref(Date.now());


const openModal = result => {
  datetopost.value = Date.now();
  isModalOpened.value = true;
  modalcontent.value = resevents
};
const closeModal = () => {
  isModalOpened.value = false;
};


const ttest = result => {

  summarizefeed(result)
}

const submitHandler = async () => {


}


</script>

<!--  font-thin bg-gradient-to-r from-white to-nostr bg-clip-text text-transparent -->

<template>

  <div class="greetings">
    <h1 class="text-7xl font-black tracking-wide">Noogle</h1>
    <h3 class="text-7xl font-black tracking-wide">Summarization</h3>

    <h3>
      <br>
      <button class="v-Button" @click="summarizefeed($props.events)">Summarize Results</button>
    </h3>

  </div>
  <br>


  <div class=" relative space-y-2">
    <div class="grid grid-cols-1 gap-2 ">

      <div v-for="dvm in store.state.summarizationdvms" :key="dvm.id"
           className="card w-70 bg-base-100 shadow-xl">


        <div className="card-body">

          <div className="playeauthor-wrapper">
            <figure className="w-20">
              <img v-if="dvm.image" :src="dvm.image" alt="DVM Picture" className="avatar"/>
              <img v-else class="avatar" src="@/assets/nostr-purple.svg"/>
            </figure>


            <h2 className="card-title">{{ dvm.name }}</h2>
          </div>
          <h3 class="fa-cut">{{ dvm.about }}</h3>


          <div className="card-actions justify-end mt-auto">

            <div className="tooltip mt-auto">


              <button
                  v-if="dvm.status !== 'finished' && dvm.status !== 'paid' && dvm.status !== 'payment-required' && dvm.status !== 'error'"
                  className="btn">{{ dvm.status }}
              </button>
              <button v-if="dvm.status === 'finished'" className="btn">Done</button>
              <button v-if="dvm.status === 'paid'" className="btn">Paid, waiting for DVM..</button>
              <button v-if="dvm.status === 'error'" className="btn">Error</button>
              <button v-if="dvm.status === 'payment-required'" className="zap-Button" @click="zap_local(dvm.bolt11);">
                {{ dvm.amount / 1000 }} Sats
              </button>


            </div>

          </div>

          <!--       <div v-if="dvm.result.length > 0" class="collapse bg-base-200">
         <input type="checkbox" class="peer" />
         <div class="collapse-title bg-primary text-primary-content peer-checked:bg-secondary peer-checked:text-secondary-content">
           Click me to show/hide content
         </div>
         <div class="collapse-content bg-primary text-primary-content peer-checked:bg-base-200 peer-checked:text-accent">

         </div>
 </div> -->
          <p v-if="dvm.status === 'finished'">{{ dvm.result }}</p>

          <!--   <details v-if="dvm.status === 'finished'" class="collapse bg-base">
          <summary class="collapse-title  "><div class="btn">Show/Hide Results</div></summary>

         <div class="collapse-content font-size-0" className="z-10" id="collapse">




            </div>
        </details>-->


        </div>

      </div>
    </div>


  </div>

</template>

<style scoped>

.zap-Button {
  @apply btn hover:bg-amber-400 border-amber-400 text-base;
  bottom: 0;
}

.v-Button {
  @apply bg-nostr hover:bg-nostr2 focus:ring-white mb-2 inline-flex flex-none items-center rounded-lg border border-black px-3 py-1.5 text-sm leading-4 text-white transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900;
  height: 48px;
  margin: 5px;
}

.c-Input {
  @apply bg-base-200 text-accent dark:bg-black dark:text-white  focus:ring-white mb-2 inline-flex flex-none items-center rounded-lg border border-transparent px-3 py-1.5 text-sm leading-4 text-accent-content transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900;

  width: 350px;
  height: 48px;

}

.d-Input {
  @apply bg-black hover:bg-gray-900 focus:ring-white mb-2 inline-flex flex-none items-center rounded-lg border border-transparent px-3 py-1.5 text-sm leading-4 text-white transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900;
  width: 300px;

  color: white;
  background: black;
}

.playeauthor-wrapper {
  padding: 6px;
  display: flex;
  align-items: center;
  justify-items: center;
}

.logo {
  display: flex;
  width: 100%;
  height: 125px;
  justify-content: center;
  align-items: center;
}

h3 {
  font-size: 1.0rem;
  text-align: left;
}


.avatar {
  margin-right: 10px;
  margin-left: 0px;
  display: inline-block;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: inset 0 4px 4px 0 rgb(0 0 0 / 10%);
}

.greetings h1,
.greetings h3 {
  text-align: left;

}

.center {
  text-align: center;
  justify-content: center;
}


@media (min-width: 1024px) {

  .greetings h1,
  .greetings h3 {
    text-align: center;
  }
}
</style>
